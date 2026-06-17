from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import StandardResultsSetPagination

from .pagination import StandardResultsSetPagination
from .permissions import RoleBasedPermission
from .serializers import (
    PatientSerializer,
    DoctorSerializer,
    AppointmentSerializer,
    MedicalRecordSerializer,
    PrescriptionSerializer,
)
from hospital.models import Patient, Doctor, Appointment, MedicalRecord, Prescription


class BaseHospitalViewSet(viewsets.ModelViewSet):
    permission_classes = [RoleBasedPermission]
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = []
    ordering_fields = []

    def get_queryset(self):
        raise NotImplementedError

    @property
    def basename(self):
        # viewset basename is used by permissions.py
        return getattr(self, "basename", self.__class__.__name__.replace("ViewSet", "").lower())


def _safe_get_related(user, attr_name):
    """Safely fetch OneToOne related object (e.g., user.patient / user.doctor)."""
    # Some user->profile relations are OneToOne and will raise
    # <User>.<rel>.RelatedObjectDoesNotExist when the related row is missing.
    try:
        return getattr(user, attr_name)
    except Exception:
        # Includes RelatedObjectDoesNotExist
        return None


class PatientViewSet(BaseHospitalViewSet):
    serializer_class = PatientSerializer

    search_fields = ["first_name", "last_name", "phone"]
    ordering_fields = ["admitted_date", "first_name", "last_name"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(getattr(user, "profile", None), "role", None)

        qs = Patient.objects.all()

        if role == "patient":
            patient_obj = _safe_get_related(user, "patient")
            return qs.none() if patient_obj is None else qs.filter(id=patient_obj.id).order_by("id")

        if role == "doctor":
            doctor_obj = _safe_get_related(user, "doctor")
            if doctor_obj is None:
                return qs.none()
            patient_ids = Appointment.objects.filter(doctor=doctor_obj).values_list("patient_id", flat=True)
            return qs.filter(id__in=patient_ids).order_by("id")

        if role == "receptionist":
            return qs.order_by("id")

        return qs.none()


class DoctorViewSet(BaseHospitalViewSet):
    serializer_class = DoctorSerializer

    search_fields = ["first_name", "last_name", "specialty"]
    ordering_fields = ["first_name", "last_name", "experience_years", "specialty"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(getattr(user, "profile", None), "role", None)

        qs = Doctor.objects.all()

        # As per earlier logic, only receptionist/admin can manage doctors.
        # Keep patient-restricted browsing denied by queryset.
        if role == "patient":
            return qs.none()

        if role == "doctor":
            # Doctors can view other doctors? Keep denied by queryset.
            return qs.none()

        if role == "receptionist":
            return qs

        return qs.none()


class AppointmentViewSet(BaseHospitalViewSet):
    serializer_class = AppointmentSerializer

    search_fields = ["patient__first_name", "patient__last_name", "doctor__first_name", "doctor__last_name"]
    ordering_fields = ["date", "time", "created_at", "status"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(getattr(user, "profile", None), "role", None)

        qs = Appointment.objects.select_related("patient", "doctor")

        if role == "patient":
            patient_obj = _safe_get_related(user, "patient")
            return qs.none() if patient_obj is None else qs.filter(patient=patient_obj)

        if role == "doctor":
            doctor_obj = _safe_get_related(user, "doctor")
            return qs.none() if doctor_obj is None else qs.filter(doctor=doctor_obj)

        if role == "receptionist":
            return qs

        return qs.none()


class MedicalRecordViewSet(BaseHospitalViewSet):
    serializer_class = MedicalRecordSerializer

    search_fields = ["diagnosis", "symptoms", "findings", "notes", "record_type"]
    ordering_fields = ["record_date"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(getattr(user, "profile", None), "role", None)

        qs = MedicalRecord.objects.select_related("patient", "doctor")

        if role == "patient":
            patient_obj = _safe_get_related(user, "patient")
            return qs.none() if patient_obj is None else qs.filter(patient=patient_obj)

        if role == "doctor":
            doctor_obj = _safe_get_related(user, "doctor")
            return qs.none() if doctor_obj is None else qs.filter(doctor=doctor_obj)

        if role == "receptionist":
            return qs.none()

        return qs.none()


class PrescriptionViewSet(BaseHospitalViewSet):
    serializer_class = PrescriptionSerializer

    search_fields = ["medicine_name", "dosage", "instructions", "notes"]
    ordering_fields = ["prescription_date", "start_date", "end_date"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(getattr(user, "profile", None), "role", None)

        qs = Prescription.objects.select_related("patient", "doctor")

        if role == "patient":
            patient_obj = _safe_get_related(user, "patient")
            return qs.none() if patient_obj is None else qs.filter(patient=patient_obj)

        if role == "doctor":
            doctor_obj = _safe_get_related(user, "doctor")
            return qs.none() if doctor_obj is None else qs.filter(doctor=doctor_obj)

        if role == "receptionist":
            return qs.none()

        return qs.none()


