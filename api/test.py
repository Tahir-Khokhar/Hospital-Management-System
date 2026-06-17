from datetime import timedelta
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from hospital.models import Profile, Patient, Doctor, Appointment, MedicalRecord, Prescription


class JWTAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="adminuser", password="pass1234")
        Profile.objects.update_or_create(user=self.user, defaults={"role": "admin"})

        self.client = APIClient()

    def test_no_auth_denied(self):
        resp = self.client.get("/api/patients/")
        self.assertIn(resp.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

    def test_login_token_obtain(self):
        resp = self.client.post("/api/token/", {"username": "adminuser", "password": "pass1234"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)


class AppointmentBookingTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="pass1234")
        Profile.objects.update_or_create(user=self.admin, defaults={"role": "admin"})


        self.doctor_user = User.objects.create_user(username="doc", password="pass1234")
        Profile.objects.update_or_create(user=self.doctor_user, defaults={"role": "doctor"})

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            first_name="John",
            last_name="Doe",
            specialty="Cardiology",
            experience_years=5,
            gender="Male",
            phone="123",
            email="doc@example.com",
        )

        self.patient_user = User.objects.create_user(username="pat", password="pass1234")
        Profile.objects.update_or_create(user=self.patient_user, defaults={"role": "patient"})

        self.patient = Patient.objects.create(
            user=self.patient_user,
            first_name="Jane",
            last_name="Smith",
            age=30,
            gender="Female",
            phone="555",
            address="x",
        )

        self.client = APIClient()

        # token
        token_resp = self.client.post("/api/token/", {"username": "admin", "password": "pass1234"})
        self.access = token_resp.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_prevent_past_appointment(self):
        past_date = (timezone.now().date() - timedelta(days=1)).isoformat()
        resp = self.client.post(
            "/api/appointments/",
            {
                "patient": self.patient.id,
                "doctor": self.doctor.id,
                "date": past_date,
                "time": "10:00:00",
                "notes": "test",
                "reminder_sent": False,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_prevent_double_booking(self):
        date_str = (timezone.now().date() + timedelta(days=1)).isoformat()

        payload = {
            "patient": self.patient.id,
            "doctor": self.doctor.id,
            "date": date_str,
            "time": "11:00:00",
            "notes": "first",
            "reminder_sent": False,
        }
        r1 = self.client.post("/api/appointments/", payload, format="json")
        if r1.status_code != 201:
            # show validation payload if present
            self.fail(f"Expected 201, got {r1.status_code}. Response: {r1.content!r} | Data: {getattr(r1, 'data', None)}")
        self.assertEqual(r1.status_code, 201)



        payload["notes"] = "second"
        r2 = self.client.post("/api/appointments/", payload, format="json")
        self.assertEqual(r2.status_code, 400)

