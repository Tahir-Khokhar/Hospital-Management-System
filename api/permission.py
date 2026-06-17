from rest_framework.permissions import BasePermission


class RoleBasedPermission(BasePermission):
    """Row-level + action-level permissions based on Profile.role."""

    message = "You do not have permission to perform this action."  # DRF will use this on 403.

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(getattr(user, "profile", None), "role", None)
        if role is None:
            # If Profile missing, deny.
            return False

        # Attach role to view for later use if needed.
        setattr(view, "user_role", role)

        # Admin: allow everything.
        if role == "admin":
            return True

        # Patients cannot create/update/delete appointment/medical resources.
        if role == "patient":
            return view.action in {"list", "retrieve"}

        # Receptionist: manage appointments + patient registration.
        if role == "receptionist":
            return view.basename in {"appointment", "patients"} or view.action in {"create", "list", "retrieve", "update", "partial_update", "destroy"}

        # Doctor: view assigned patients + manage prescriptions.
        if role == "doctor":
            if view.basename == "prescriptions":
                return True  # full CRUD
            return view.action in {"list", "retrieve"}  # read-only for everything else

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        role = getattr(getattr(user, "profile", None), "role", None)

        if role == "admin":
            return True

        if role == "patient":
            # Patient can only access their own objects.
            # Appointment
            if view.basename == "appointments":
                return getattr(obj, "patient_id", None) and obj.patient.user_id == user.id
            # MedicalRecord
            if view.basename == "medical-records":
                return getattr(obj, "patient_id", None) and obj.patient.user_id == user.id
            # Prescriptions
            if view.basename == "prescriptions":
                return getattr(obj, "patient_id", None) and obj.patient.user_id == user.id
            return False

        if role == "doctor":
            # Doctors can access assigned patients' info.
            if view.basename in {"appointments", "medical-records"}:
                # obj is Appointment or MedicalRecord: filter by doctor.
                return getattr(obj, "doctor_id", None) and obj.doctor.user_id == user.id
            if view.basename == "prescriptions":
                return getattr(obj, "doctor_id", None) and obj.doctor.user_id == user.id
            return False

        if role == "receptionist":
            # Receptionists can manage appointments and patient registration.
            if view.basename == "appointments":
                return True
            if view.basename == "patients":
                return True
            return False

        return False

