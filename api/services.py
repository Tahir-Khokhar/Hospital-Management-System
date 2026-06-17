from django.utils import timezone
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from hospital.models import Appointment, Patient, Doctor


def validate_appointment_payload(*, patient: Patient, doctor: Doctor, date, time, ignore_appointment_id=None):
    # Prevent appointments in the past
    # Combine date+time as local-aware datetime (timezone-aware).
    appt_dt = timezone.make_aware(timezone.datetime.combine(date, time))
    if appt_dt < timezone.now():
        raise ValidationError({"non_field_errors": ["Appointments cannot be in the past."]})

    # Prevent double booking for the same doctor at same date/time
    qs = Appointment.objects.filter(patient=patient, doctor=doctor, date=date, time=time)
    if ignore_appointment_id is not None:
        qs = qs.exclude(id=ignore_appointment_id)
    if qs.exists():
        raise ValidationError({"non_field_errors": ["This doctor already has an appointment at the selected date/time."]})


def validate_patient_doctor_relationship(*, patient: Patient, doctor: Doctor):
    # Doctor/patient relationship validation depends on your data model.
    # Current DB model has no explicit assignment table; appointments and records imply relationship.
    # We'll ensure both records exist (handled by serializer fields) and rely on appointment linkage.
    # If you later add a doctor-patient assignment model, enforce here.
    if not patient.user_id:
        raise ValidationError({"non_field_errors": ["Invalid patient." ]})
    if not doctor.user_id:
        raise ValidationError({"non_field_errors": ["Invalid doctor." ]})

