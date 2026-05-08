from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('receptionist', 'Receptionist'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male')
    specialty = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    phone = models.CharField(max_length=15)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    medical_history = models.TextField(blank=True)
    admitted_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Room(models.Model):
    ROOM_TYPES = [
        ('general', 'General Ward'),
        ('private', 'Private Room'),
        ('icu', 'ICU'),
        ('operation', 'Operation Theater'),
        ('emergency', 'Emergency Room'),
    ]
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    floor = models.PositiveIntegerField(default=1)
    capacity = models.PositiveIntegerField(default=1)
    is_occupied = models.BooleanField(default=False)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()})"

class Bed(models.Model):
    BED_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('reserved', 'Reserved'),
    ]
    bed_number = models.CharField(max_length=10)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    status = models.CharField(max_length=20, choices=BED_STATUS, default='available')
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='beds')

    def __str__(self):
        return f"Bed {self.bed_number} - {self.room}"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    reminder_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment: {self.patient} with {self.doctor}"

class Operation(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='operations')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='operations')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    operation_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_date = models.DateTimeField()
    duration_hours = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.operation_name} - {self.patient}"

class Treatment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='treatments')
    treatment_name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    medications = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.treatment_name} - {self.patient}"

class LabTest(models.Model):
    TEST_TYPES = [
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('xray', 'X-Ray'),
        ('mri', 'MRI Scan'),
        ('ct', 'CT Scan'),
        ('ultrasound', 'Ultrasound'),
        ('ecg', 'ECG'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    test_type = models.CharField(max_length=20, choices=TEST_TYPES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    scheduled_date = models.DateField(default=timezone.now)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.get_test_type_display()} - {self.patient}"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    invoice_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL, null=True, blank=True)
    treatment = models.ForeignKey(Treatment, on_delete=models.SET_NULL, null=True, blank=True)
    room_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    medication_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def calculate_total(self):
        total = self.room_charges + self.medication_charges + self.other_charges
        if self.appointment:
            total += 100
        if self.operation:
            total += self.operation.cost
        if self.treatment:
            total += self.treatment.cost
        return total

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.patient}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('app', 'In-App'),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.notification_type} to {self.recipient.username}: {self.subject}"

class Staff(models.Model):
    STAFF_TYPES = [
        ('nurse', 'Nurse'),
        ('wardboy', 'Ward Boy'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    age = models.PositiveIntegerField(default=25)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    joining_date = models.DateField(auto_now_add=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    shift = models.CharField(max_length=20, choices=[('morning', 'Morning'), ('evening', 'Evening'), ('night', 'Night')], default='morning')

    class Meta:
        verbose_name_plural = 'Staff'
        ordering = ['name']

def __str__(self):
        return f"{self.name}"

# ==================== Phase 1: Medical Records Module ====================

class MedicalRecord(models.Model):
    """Patient medical history and records"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_records')
    record_date = models.DateField(auto_now_add=True)
    record_type = models.CharField(max_length=50, choices=[
        ('diagnosis', 'Diagnosis'),
        ('consultation', 'Consultation'),
        ('followup', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('routine', 'Routine Checkup'),
    ])
    diagnosis = models.CharField(max_length=200)
    symptoms = models.TextField(blank=True)
    findings = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Record #{self.id} - {self.patient} - {self.record_type}"


class Allergy(models.Model):
    """Patient allergies tracking"""
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('life_threatening', 'Life Threatening'),
    ]
    TYPE_CHOICES = [
        ('drug', 'Drug'),
        ('food', 'Food'),
        ('environmental', 'Environmental'),
        ('other', 'Other'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=100)
    allergy_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    reactions = models.TextField(blank=True)
    discovered_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.allergen} - {self.patient} ({self.severity})"


class VitalSign(models.Model):
    """Patient vital signs records"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    recorded_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    # Vital signs fields
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True, help_text="mmHg")
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True, help_text="mmHg")
    heart_rate = models.PositiveIntegerField(null=True, blank=True, help_text="bpm")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="F")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="breaths per minute")
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True, help_text="%")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="cm")
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Vitals {self.recorded_at} - {self.patient}"


class Prescription(models.Model):
    """Medical prescriptions"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    prescription_date = models.DateField(auto_now_add=True)
    
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50, help_text="e.g., twice daily")
    duration = models.CharField(max_length=50, help_text="e.g., 7 days")
    instructions = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_fulfilled = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
def __str__(self):
        return f"{self.medicine_name} - {self.patient}"

# ==================== Phase 2: Pharmacy Module ====================

class MedicineCategory(models.Model):
    """Medicine categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Medicine(models.Model):
    """Medicine inventory"""
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(MedicineCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicines')
    generic_name = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    
    # Inventory
    quantity_in_stock = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, help_text="e.g., tablets, ml, vials")
    reorder_level = models.PositiveIntegerField(default=10)
    
    # Pricing
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Info
    description = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} ({self.quantity_in_stock} {self.unit})"
    
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level


class PharmacyOrder(models.Model):
    """Pharmacy orders for patients"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('dispensed', 'Dispensed'),
        ('cancelled', 'Cancelled'),
    ]
    order_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='pharmacy_orders')
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ordered_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    dispensed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'staff_type': 'nurse'})
    order_date = models.DateTimeField(default=timezone.now)
    dispensed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
def __str__(self):
        return f"Order #{self.order_number} - {self.medicine}"

# ==================== Phase 3: Emergency Management ====================

class EmergencyContact(models.Model):
    """Patient emergency contacts"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.patient}"


class Ambulance(models.Model):
    """Ambulance tracking"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('dispatched', 'Dispatched'),
        ('returning', 'Returning'),
        ('maintenance', 'Maintenance'),
        ('out_of_service', 'Out of Service'),
    ]
    vehicle_number = models.CharField(max_length=20, unique=True)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    current_location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Ambulance {self.vehicle_number} - {self.status}"


class EmergencyAdmission(models.Model):
    """Emergency admissions"""
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('urgent', 'Urgent'),
        ('stable', 'Stable'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_admissions')
    emergency_contact = models.ForeignKey(EmergencyContact, on_delete=models.SET_NULL, null=True, blank=True)
    ambulance = models.ForeignKey(Ambulance, on_delete=models.SET_NULL, null=True, blank=True)
    
    admission_time = models.DateTimeField(default=timezone.now)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='stable')
    reason = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    initial_diagnosis = models.CharField(max_length=200, blank=True)
    admitted_to = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    is_discharged = models.BooleanField(default=False)
    discharge_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Emergency #{self.id} - {self.patient} ({self.priority})"

# ==================== Phase 4: Insurance & Billing ====================

class InsuranceProvider(models.Model):
    """Insurance providers"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class InsurancePolicy(models.Model):
    """Patient insurance policies"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_policies')
    provider = models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE, related_name='policies')
    policy_number = models.CharField(max_length=50, unique=True)
    holder_name = models.CharField(max_length=100)
    holder_relationship = models.CharField(max_length=50, blank=True)
    
    start_date = models.DateField()
    end_date = models.DateField()
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    coverage_type = models.CharField(max_length=50, choices=[
        ('individual', 'Individual'),
        ('family', 'Family'),
        ('group', 'Group'),
    ])
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Policy #{self.policy_number} - {self.patient}"


class InsuranceClaim(models.Model):
    """Insurance claims"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partial Approval'),
        ('paid', 'Paid'),
    ]
    claim_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_claims')
    policy = models.ForeignKey(InsurancePolicy, on_delete=models.CASCADE, related_name='claims')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    claim_date = models.DateField(default=timezone.now)
    review_date = models.DateField(null=True, blank=True)
    processed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Claim #{self.claim_number} - {self.patient}"


class PaymentPlan(models.Model):
    """Payment plans for patients"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('cancelled', 'Cancelled'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payment_plans')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payment_plans')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    next_payment_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Payment Plan #{self.id} - {self.patient}"

# ==================== Phase 5: Additional Features ====================

class AuditLog(models.Model):
    """Track user actions for audit"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.action} - {self.model_name} by {self.user}"


class Document(models.Model):
    """Document uploads"""
    DOC_TYPES = [
        ('report', 'Medical Report'),
        ('prescription', 'Prescription'),
        ('lab_result', 'Lab Result'),
        ('insurance', 'Insurance Document'),
        ('id_proof', 'ID Proof'),
        ('other', 'Other'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    document_type = models.CharField(max_length=20, choices=DOC_TYPES)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.title} - {self.document_type}"
