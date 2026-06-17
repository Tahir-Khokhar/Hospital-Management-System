from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    PatientViewSet,
    DoctorViewSet,
    AppointmentViewSet,
    MedicalRecordViewSet,
    PrescriptionViewSet,
)

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patients")
router.register(r"doctors", DoctorViewSet, basename="doctors")
router.register(r"appointments", AppointmentViewSet, basename="appointments")
router.register(r"medical-records", MedicalRecordViewSet, basename="medical-records")
router.register(r"prescriptions", PrescriptionViewSet, basename="prescriptions")

urlpatterns = [
    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # OpenAPI / Swagger
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # APIs
    path("", include(router.urls)),
]

