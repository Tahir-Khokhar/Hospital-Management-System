from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Home
    path('', views.home, name='home'),
    
    # Patient Portal
    path('patient-portal/', views.patient_portal, name='patient_portal'),
    
    # Doctor Portal
    path('doctor-portal/', views.doctor_portal, name='doctor_portal'),
    
    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    
    # Doctors
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/update-status/', views.update_appointment_status, name='update_appointment_status'),
    
    # Rooms
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/add/', views.add_room, name='add_room'),
    
    # Beds
    path('beds/', views.bed_list, name='bed_list'),
    
    # Operations
    path('operations/', views.operation_list, name='operation_list'),
    path('operations/add/', views.add_operation, name='add_operation'),
    
    # Treatments
    path('treatments/', views.treatment_list, name='treatment_list'),
    path('treatments/add/', views.add_treatment, name='add_treatment'),
    
    # Lab Tests
    path('lab-tests/', views.lab_test_list, name='lab_test_list'),
    path('lab-tests/add/', views.add_lab_test, name='add_lab_test'),
    
    # Billing
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/add/', views.add_invoice, name='add_invoice'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Charts API
    path('api/chart-data/', views.chart_data, name='chart_data'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Patient Map
    path('patient-map/', views.patient_map, name='patient_map'),
    
# Staff
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.add_staff, name='add_staff'),
    
    # Medical Records
    path('medical-records/', views.medical_record_list, name='medical_record_list'),
    path('medical-records/add/', views.add_medical_record, name='add_medical_record'),
    
    # Allergies
    path('allergies/', views.allergy_list, name='allergy_list'),
    path('allergies/add/', views.add_allergy, name='add_allergy'),
    path('allergies/<int:pk>/', views.allergy_detail, name='allergy_detail'),
    path('allergies/<int:pk>/edit/', views.allergy_edit, name='allergy_edit'),
    path('allergies/<int:pk>/delete/', views.allergy_delete, name='allergy_delete'),
    
    # Vital Signs
    path('vital-signs/', views.vital_sign_list, name='vital_sign_list'),
    path('vital-signs/add/', views.add_vital_sign, name='add_vital_sign'),
    
    # Prescriptions
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/add/', views.add_prescription, name='add_prescription'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('prescriptions/<int:pk>/edit/', views.prescription_edit, name='prescription_edit'),
    path('prescriptions/<int:pk>/delete/', views.prescription_delete, name='prescription_delete'),
    
    # Pharmacy
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/add/', views.add_medicine, name='add_medicine'),
    path('pharmacy-orders/', views.pharmacy_order_list, name='pharmacy_order_list'),
    path('pharmacy-orders/add/', views.add_pharmacy_order, name='add_pharmacy_order'),
    
    # Emergency
    path('ambulances/', views.ambulance_list, name='ambulance_list'),
    path('ambulances/add/', views.add_ambulance, name='add_ambulance'),
    path('emergency-admissions/', views.emergency_admission_list, name='emergency_admission_list'),
    path('emergency-admissions/add/', views.add_emergency_admission, name='add_emergency_admission'),
    
    # Insurance
    path('insurance-providers/', views.insurance_provider_list, name='insurance_provider_list'),
    path('insurance-providers/add/', views.add_insurance_provider, name='add_insurance_provider'),
    path('insurance-policies/', views.insurance_policy_list, name='insurance_policy_list'),
    path('insurance-policies/add/', views.add_insurance_policy, name='add_insurance_policy'),
    path('insurance-claims/', views.insurance_claim_list, name='insurance_claim_list'),
    path('insurance-claims/add/', views.add_insurance_claim, name='add_insurance_claim'),
    path('payment-plans/', views.payment_plan_list, name='payment_plan_list'),
    path('payment-plans/add/', views.add_payment_plan, name='add_payment_plan'),
    path('payment-plans/<int:pk>/', views.payment_plan_detail, name='payment_plan_detail'),
    path('payment-plans/<int:pk>/edit/', views.payment_plan_edit, name='payment_plan_edit'),
    path('payment-plans/<int:pk>/delete/', views.payment_plan_delete, name='payment_plan_delete'),
    
    # Audit Logs
    path('audit-logs/', views.audit_log_list, name='audit_log_list'),
    
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/add/', views.add_document, name='add_document'),
]
