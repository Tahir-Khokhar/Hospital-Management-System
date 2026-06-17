from django.contrib.auth.models import User
from rest_framework import serializers

from hospital.models import Appointment, Patient, Doctor, MedicalRecord, Prescription
from .services import (
    validate_appointment_payload,
    validate_patient_doctor_relationship,
)


def _get_user_role(user: User):
    try:
        return user.profile.role
    except Exception:
        return None


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "first_name",
            "last_name",
            "age",
            "gender",
            "phone",
            "address",
            "latitude",
            "longitude",
            "medical_history",
            "admitted_date",
        ]


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "specialty",
            "experience_years",
            "phone",
            "email",
            "bio",
            "is_available",
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "date",
            "time",
            "status",
            "notes",
            "created_at",
            "reminder_sent",
        ]
        read_only_fields = ["status", "created_at", "reminder_sent"]

    def validate(self, attrs):
        patient = attrs.get("patient")
        doctor = attrs.get("doctor")
        date = attrs.get("date")
        time = attrs.get("time")

        if patient is None or doctor is None or date is None or time is None:
            return attrs

        validate_patient_doctor_relationship(patient=patient, doctor=doctor)

        # Past + double booking
        ignore_id = getattr(self.instance, "id", None)
        validate_appointment_payload(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            ignore_appointment_id=ignore_id,
        )

        # Ensure doctor is available / optional rule
        # If your workflow requires availability, enforce it here.
        if hasattr(doctor, "is_available") and doctor.is_available is False:
            raise serializers.ValidationError({"non_field_errors": ["Selected doctor is not available."]})


        # Role-level relationship checks beyond object permissions
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            role = _get_user_role(request.user)
            if role == "patient":
                patient_user = patient.user
                if patient_user != request.user:
                    raise serializers.ValidationError({"non_field_errors": ["You can only book your own appointments."]})
            if role == "doctor":
                # Doctor role: appointment must use themselves
                if doctor.user != request.user:
                    raise serializers.ValidationError({"non_field_errors": ["You can only book appointments for your own schedule."]})

        return attrs


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), allow_null=True, required=False)

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient",
            "doctor",
            "record_date",
            "record_type",
            "diagnosis",
            "symptoms",
            "findings",
            "notes",
            "follow_up_date",
            "is_active",
        ]
        read_only_fields = ["record_date"]


class PrescriptionSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = Prescription
        fields = [
            "id",
            "patient",
            "doctor",
            "prescription_date",
            "medicine_name",
            "dosage",
            "frequency",
            "duration",
            "instructions",
            "start_date",
            "end_date",
            "is_active",
            "is_fulfilled",
            "notes",
        ]
        read_only_fields = ["prescription_date", "is_fulfilled"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            role = _get_user_role(request.user)
            if role == "doctor":
                # Doctor may only prescribe themselves.
                doctor = attrs.get("doctor")
                if doctor and doctor.user != request.user:
                    raise serializers.ValidationError({"non_field_errors": ["You can only create prescriptions for yourself."]})
            if role == "patient":
                patient = attrs.get("patient")
                if patient and patient.user != request.user:
                    raise serializers.ValidationError({"non_field_errors": ["You can only view your own prescriptions."]})
        return attrs


