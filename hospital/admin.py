from django.contrib import admin
from .models import (Profile, Doctor, Patient, Room, Bed, Appointment, 
                     Operation, Treatment, LabTest, Invoice, Notification, Staff,
                     MedicalRecord, Allergy, VitalSign, Prescription,
                     MedicineCategory, Medicine, PharmacyOrder,
                     EmergencyContact, Ambulance, EmergencyAdmission,
                     InsuranceProvider, InsurancePolicy, InsuranceClaim, PaymentPlan,
                     AuditLog, Document)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    list_filter = ['role']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'age', 'gender', 'phone', 'admitted_date']
    list_filter = ['gender', 'admitted_date']
    search_fields = ['first_name', 'last_name', 'phone', 'address']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'specialty', 'experience_years', 'phone', 'email', 'is_available']
    list_filter = ['specialty', 'is_available']
    search_fields = ['first_name', 'last_name', 'specialty', 'phone']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'floor', 'capacity', 'is_occupied', 'price_per_day']
    list_filter = ['room_type', 'is_occupied']

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['bed_number', 'room', 'status', 'patient']
    list_filter = ['status']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'time', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name']

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['operation_name', 'patient', 'doctor', 'scheduled_date', 'status']
    list_filter = ['status']

@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['treatment_name', 'patient', 'doctor', 'start_date', 'cost']

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['test_type', 'patient', 'status', 'scheduled_date', 'cost']
    list_filter = ['test_type', 'status']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient', 'total_amount', 'status', 'created_at']
    list_filter = ['status']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'subject', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'staff_type', 'gender', 'age', 'phone', 'salary', 'shift', 'is_active']
    list_filter = ['staff_type', 'gender', 'shift', 'is_active']
    search_fields = ['name', 'phone', 'address']

# New Models Admin Registrations

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'record_date', 'record_type', 'diagnosis']
    list_filter = ['record_type', 'record_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis']

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ['patient', 'allergen', 'allergy_type', 'severity', 'is_active']
    list_filter = ['allergy_type', 'severity', 'is_active']
    search_fields = ['patient__first_name', 'patient__last_name', 'allergen']

@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ['patient', 'recorded_at', 'blood_pressure_systolic', 'heart_rate', 'temperature']
    list_filter = ['recorded_at']
    search_fields = ['patient__first_name', 'patient__last_name']

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'medicine_name', 'dosage', 'is_active', 'is_fulfilled']
    list_filter = ['is_active', 'is_fulfilled']
    search_fields = ['patient__first_name', 'patient__last_name', 'medicine_name']

@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity_in_stock', 'unit', 'cost_per_unit', 'selling_price_per_unit', 'expiry_date']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'generic_name']

@admin.register(PharmacyOrder)
class PharmacyOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'patient', 'medicine', 'quantity', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['order_number', 'patient__first_name', 'patient__last_name']

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['patient', 'name', 'relationship', 'phone', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['patient__first_name', 'patient__last_name', 'name']

@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'driver_name', 'driver_phone', 'status', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['vehicle_number', 'driver_name']

@admin.register(EmergencyAdmission)
class EmergencyAdmissionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'admission_time', 'priority', 'reason', 'is_discharged']
    list_filter = ['priority', 'is_discharged']
    search_fields = ['patient__first_name', 'patient__last_name']

@admin.register(InsuranceProvider)
class InsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']

@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ['patient', 'provider', 'policy_number', 'coverage_amount', 'coverage_type', 'is_active']
    list_filter = ['coverage_type', 'is_active']
    search_fields = ['policy_number', 'patient__first_name', 'patient__last_name']

@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ['claim_number', 'patient', 'policy', 'claim_amount', 'status', 'claim_date']
    list_filter = ['status', 'claim_date']
    search_fields = ['claim_number', 'patient__first_name', 'patient__last_name']

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ['patient', 'invoice', 'total_amount', 'monthly_payment', 'next_payment_date', 'status']
    list_filter = ['status']
    search_fields = ['patient__first_name', 'patient__last_name']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'model_name', 'description']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'document_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
