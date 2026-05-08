from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import random
from .models import (Profile, Doctor, Patient, Room, Bed, Appointment, 
                     Operation, Treatment, LabTest, Invoice, Notification, Staff,
                     MedicalRecord, Allergy, VitalSign, Prescription,
                     MedicineCategory, Medicine, PharmacyOrder,
                     EmergencyContact, Ambulance, EmergencyAdmission,
                     InsuranceProvider, InsurancePolicy, InsuranceClaim, PaymentPlan,
                     AuditLog, Document)

def to_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def to_decimal(value, default=0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'hospital/login.html')

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'patient')
        
        if not username or not email or not password:
            messages.error(request, 'Please fill in all required fields')
            return render(request, 'hospital/register.html')
            
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'hospital/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'hospital/register.html')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.profile.role = role
        user.profile.save()
        login(request, user)

        return redirect('home')
    return render(request, 'hospital/register.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

def get_user_role(user):
    if not user.is_authenticated:
        return 'guest'
    try:
        return user.profile.role
    except Profile.DoesNotExist:
        return 'patient'


def home(request):
    user_role = get_user_role(request.user)
    
    # Statistics for dashboard
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    total_rooms = Room.objects.count()
    total_beds = Bed.objects.count()
    available_beds = Bed.objects.filter(status='available').count()
    total_operations = Operation.objects.count()
    total_treatments = Treatment.objects.count()
    total_lab_tests = LabTest.objects.count()
    total_invoices = Invoice.objects.count()
    pending_invoices = Invoice.objects.filter(status='pending').count()
    total_revenue = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Today's stats
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(date=today).count()
    today_operations = Operation.objects.filter(scheduled_date__date=today).count()
    
    # Recent activity
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:5]
    recent_operations = Operation.objects.select_related('patient', 'doctor').order_by('-created_at')[:5]
    recent_invoices = Invoice.objects.select_related('patient').order_by('-created_at')[:5]
    
    # Notifications
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    else:
        notifications = []
    
    total_staff = Staff.objects.count()
    
    context = {
        'user_role': user_role,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_staff': total_staff,
        'total_appointments': total_appointments,
        'total_rooms': total_rooms,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'total_operations': total_operations,
        'total_treatments': total_treatments,
        'total_lab_tests': total_lab_tests,
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'total_revenue': total_revenue,
        'today_appointments': today_appointments,
        'today_operations': today_operations,
        'recent_appointments': recent_appointments,
        'recent_operations': recent_operations,
        'recent_invoices': recent_invoices,
        'notifications': notifications,
    }
    return render(request, 'hospital/home.html', context)

# Patient Views
@login_required
def patient_list(request):
    user_role = get_user_role(request.user)
    if user_role == 'patient':
        # Patient can only see their own record
        try:
            patient = request.user.patient
            return redirect('patient_detail', pk=patient.pk)
        except Patient.DoesNotExist:
            messages.error(request, 'No patient record found')
            return redirect('home')
    
    query = request.GET.get('q', '')
    if query:
        patients = Patient.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(phone__icontains=query)
        )
    else:
        patients = Patient.objects.all()
    return render(request, 'hospital/patient_list.html', {'patients': patients, 'query': query, 'user_role': user_role})

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    user_role = get_user_role(request.user)
    
    # Check permissions
    if user_role == 'patient':
        try:
            if request.user.patient != patient:
                messages.error(request, 'Access denied')
                return redirect('home')
        except Patient.DoesNotExist:
            messages.error(request, 'Access denied')
            return redirect('home')
    
    appointments = patient.appointments.select_related('doctor').all()
    operations = patient.operations.select_related('doctor').all()
    treatments = patient.treatments.select_related('doctor').all()
    lab_tests = patient.lab_tests.all()
    invoices = patient.invoices.all()
    beds = patient.beds.select_related('room').all()
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'operations': operations,
        'treatments': treatments,
        'lab_tests': lab_tests,
        'invoices': invoices,
        'beds': beds,
        'user_role': user_role,
    }
    return render(request, 'hospital/patient_detail.html', context)

@login_required
def add_patient(request):
    user_role = get_user_role(request.user)
    if user_role == 'patient':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        Patient.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            age=request.POST['age'],
            gender=request.POST['gender'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            latitude=request.POST.get('latitude') or None,
            longitude=request.POST.get('longitude') or None,
            medical_history=request.POST.get('medical_history', '')
        )
        messages.success(request, 'Patient added successfully!')
        return redirect('patient_list')
    return render(request, 'hospital/add_patient.html', {'user_role': user_role})

# Doctor Views
@login_required
def doctor_list(request):
    user_role = get_user_role(request.user)
    query = request.GET.get('q', '')
    if query:
        doctors = Doctor.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(specialty__icontains=query)
        )
    else:
        doctors = Doctor.objects.all()
    return render(request, 'hospital/doctor_list.html', {'doctors': doctors, 'query': query, 'user_role': user_role})

@login_required
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    user_role = get_user_role(request.user)
    
    # Check permissions
    if user_role == 'doctor':
        try:
            if request.user.doctor != doctor:
                messages.error(request, 'Access denied')
                return redirect('home')
        except Doctor.DoesNotExist:
            messages.error(request, 'Access denied')
            return redirect('home')
    
    appointments = doctor.appointments.select_related('patient').all()
    operations = doctor.operations.select_related('patient').all()
    treatments = doctor.treatments.select_related('patient').all()
    
    context = {
        'doctor': doctor,
        'appointments': appointments,
        'operations': operations,
        'treatments': treatments,
        'user_role': user_role,
    }
    return render(request, 'hospital/doctor_detail.html', context)

@login_required
def add_doctor(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        Doctor.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            specialty=request.POST['specialty'],
            experience_years=to_int(request.POST.get('experience_years'), 0),
            phone=request.POST['phone'],
            email=request.POST['email'],
            bio=request.POST.get('bio', '')
        )
        messages.success(request, 'Doctor added successfully!')
        return redirect('doctor_list')
    return render(request, 'hospital/add_doctor.html', {'user_role': user_role})

# Appointment Views
@login_required
def appointment_list(request):
    user_role = get_user_role(request.user)
    query = request.GET.get('q', '')
    
    if user_role == 'patient':
        try:
            patient = request.user.patient
            appointments = Appointment.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            appointments = Appointment.objects.none()
    elif user_role == 'doctor':
        try:
            doctor = request.user.doctor
            appointments = Appointment.objects.filter(doctor=doctor)
        except Doctor.DoesNotExist:
            appointments = Appointment.objects.none()
    else:
        appointments = Appointment.objects.all()
    
    if query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=query) | 
            Q(doctor__first_name__icontains=query)
        )
    
    appointments = appointments.select_related('patient', 'doctor').order_by('-date', '-time')
    return render(request, 'hospital/appointment_list.html', {'appointments': appointments, 'query': query, 'user_role': user_role})

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user_role = get_user_role(request.user)
    
    # Permission check
    if user_role == 'patient' and appointment.patient.user != request.user:
        messages.error(request, 'Access denied')
        return redirect('home')
    if user_role == 'doctor' and appointment.doctor.user != request.user:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    return render(request, 'hospital/appointment_detail.html', {'appointment': appointment, 'user_role': user_role})

@login_required
def add_appointment(request):
    user_role = get_user_role(request.user)
    
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        doctor = get_object_or_404(Doctor, pk=request.POST['doctor'])
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=request.POST['date'],
            time=request.POST['time'],
            notes=request.POST.get('notes', '')
        )
        # Create notification
        Notification.objects.create(
            recipient=patient.user if patient.user else request.user,
            notification_type='app',
            subject='New Appointment Scheduled',
            message=f'Appointment with Dr. {doctor} on {appointment.date} at {appointment.time}'
        )
        messages.success(request, 'Appointment scheduled successfully!')
        return redirect('appointment_list')
    
    patients = Patient.objects.all()
    doctors = Doctor.objects.filter(is_available=True)
    
    if user_role == 'patient':
        try:
            patients = Patient.objects.filter(pk=request.user.patient.pk)
        except Patient.DoesNotExist:
            patients = Patient.objects.none()
    
    return render(request, 'hospital/add_appointment.html', {'patients': patients, 'doctors': doctors, 'user_role': user_role})

@login_required
def update_appointment_status(request, pk):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.status = request.POST['status']
        appointment.save()
        messages.success(request, 'Status updated successfully!')
    return redirect('appointment_detail', pk=pk)

# Room Views
@login_required
def room_list(request):
    user_role = get_user_role(request.user)
    rooms = Room.objects.prefetch_related('beds').all()
    return render(request, 'hospital/room_list.html', {'rooms': rooms, 'user_role': user_role})

@login_required
def add_room(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        room = Room.objects.create(
            room_number=request.POST['room_number'],
            room_type=request.POST['room_type'],
            floor=to_int(request.POST.get('floor'), 1),
            capacity=to_int(request.POST.get('capacity'), 1),
            price_per_day=to_decimal(request.POST.get('price_per_day'), 0.00)
        )
        # Create beds
        for i in range(1, room.capacity + 1):
            Bed.objects.create(bed_number=f"{room.room_number}-{i}", room=room)
        messages.success(request, 'Room and beds added successfully!')
        return redirect('room_list')
    return render(request, 'hospital/add_room.html', {'user_role': user_role})

# Bed Views
@login_required
def bed_list(request):
    user_role = get_user_role(request.user)
    beds = Bed.objects.select_related('room', 'patient').all()
    return render(request, 'hospital/bed_list.html', {'beds': beds, 'user_role': user_role})

# Operation Views
@login_required
def operation_list(request):
    user_role = get_user_role(request.user)
    query = request.GET.get('q', '')
    
    if user_role == 'patient':
        try:
            operations = Operation.objects.filter(patient=request.user.patient)
        except Patient.DoesNotExist:
            operations = Operation.objects.none()
    elif user_role == 'doctor':
        try:
            operations = Operation.objects.filter(doctor=request.user.doctor)
        except Doctor.DoesNotExist:
            operations = Operation.objects.none()
    else:
        operations = Operation.objects.all()
    
    if query:
        operations = operations.filter(operation_name__icontains=query)
    
    operations = operations.select_related('patient', 'doctor', 'room').order_by('-scheduled_date')
    return render(request, 'hospital/operation_list.html', {'operations': operations, 'query': query, 'user_role': user_role})

@login_required
def add_operation(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        doctor = get_object_or_404(Doctor, pk=request.POST['doctor'])
        room = get_object_or_404(Room, pk=request.POST['room']) if request.POST.get('room') else None
        
        operation = Operation.objects.create(
            patient=patient,
            doctor=doctor,
            room=room,
            operation_name=request.POST['operation_name'],
            description=request.POST.get('description', ''),
            scheduled_date=request.POST['scheduled_date'],
            duration_hours=to_int(request.POST.get('duration_hours'), 1),
            cost=to_decimal(request.POST.get('cost'), 0)
        )
        messages.success(request, 'Operation scheduled successfully!')
        return redirect('operation_list')
    
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    rooms = Room.objects.filter(room_type='operation')
    return render(request, 'hospital/add_operation.html', {'patients': patients, 'doctors': doctors, 'rooms': rooms, 'user_role': user_role})

# Treatment Views
@login_required
def treatment_list(request):
    user_role = get_user_role(request.user)
    
    if user_role == 'patient':
        try:
            treatments = Treatment.objects.filter(patient=request.user.patient)
        except Patient.DoesNotExist:
            treatments = Treatment.objects.none()
    elif user_role == 'doctor':
        try:
            treatments = Treatment.objects.filter(doctor=request.user.doctor)
        except Doctor.DoesNotExist:
            treatments = Treatment.objects.none()
    else:
        treatments = Treatment.objects.all()
    
    treatments = treatments.select_related('patient', 'doctor').order_by('-created_at')
    return render(request, 'hospital/treatment_list.html', {'treatments': treatments, 'user_role': user_role})

@login_required
def add_treatment(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        doctor = get_object_or_404(Doctor, pk=request.POST['doctor'])
        Treatment.objects.create(
            patient=patient,
            doctor=doctor,
            treatment_name=request.POST['treatment_name'],
            description=request.POST['description'],
            start_date=request.POST['start_date'],
            end_date=request.POST.get('end_date') or None,
            medications=request.POST.get('medications', ''),
            instructions=request.POST.get('instructions', ''),
            cost=to_decimal(request.POST.get('cost'), 0)
        )
        messages.success(request, 'Treatment added successfully!')
        return redirect('treatment_list')
    
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    return render(request, 'hospital/add_treatment.html', {'patients': patients, 'doctors': doctors, 'user_role': user_role})

# Lab Test Views
@login_required
def lab_test_list(request):
    user_role = get_user_role(request.user)
    
    if user_role == 'patient':
        try:
            tests = LabTest.objects.filter(patient=request.user.patient)
        except Patient.DoesNotExist:
            tests = LabTest.objects.none()
    else:
        tests = LabTest.objects.all()
    
    tests = tests.select_related('patient').order_by('-created_at')
    return render(request, 'hospital/lab_test_list.html', {'tests': tests, 'user_role': user_role})

@login_required
def add_lab_test(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        LabTest.objects.create(
            patient=patient,
            test_type=request.POST['test_type'],
            description=request.POST.get('description', ''),
            scheduled_date=request.POST['scheduled_date'],
            cost=to_decimal(request.POST.get('cost'), 0)
        )
        messages.success(request, 'Lab test added successfully!')
        return redirect('lab_test_list')
    
    patients = Patient.objects.all()
    return render(request, 'hospital/add_lab_test.html', {'patients': patients, 'user_role': user_role})

# Billing Views
@login_required
def invoice_list(request):
    user_role = get_user_role(request.user)
    
    if user_role == 'patient':
        try:
            invoices = Invoice.objects.filter(patient=request.user.patient)
        except Patient.DoesNotExist:
            invoices = Invoice.objects.none()
    else:
        invoices = Invoice.objects.all()
    
    invoices = invoices.select_related('patient').order_by('-created_at')
    return render(request, 'hospital/invoice_list.html', {'invoices': invoices, 'user_role': user_role})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    user_role = get_user_role(request.user)
    
    if user_role == 'patient' and invoice.patient.user != request.user:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    return render(request, 'hospital/invoice_detail.html', {'invoice': invoice, 'user_role': user_role})

@login_required
def add_invoice(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        invoice = Invoice.objects.create(
            invoice_number=request.POST['invoice_number'],
            patient=patient,
            room_charges=to_decimal(request.POST.get('room_charges'), 0),
            medication_charges=to_decimal(request.POST.get('medication_charges'), 0),
            other_charges=to_decimal(request.POST.get('other_charges'), 0),
            due_date=request.POST['due_date'],
            notes=request.POST.get('notes', '')
        )
        invoice.total_amount = invoice.calculate_total()
        invoice.save()
        messages.success(request, 'Invoice created successfully!')
        return redirect('invoice_list')
    
    patients = Patient.objects.all()
    return render(request, 'hospital/add_invoice.html', {'patients': patients, 'user_role': user_role})

# Reports & Analytics
@login_required
def reports(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    # Monthly statistics
    today = timezone.now()
    months = []
    patient_counts = []
    appointment_counts = []
    revenue_data = []
    
    for i in range(6):
        month_date = today - timedelta(days=30*i)
        month_label = month_date.strftime('%b %Y')
        months.insert(0, month_label)
        
        patient_counts.insert(0, Patient.objects.filter(admitted_date__month=month_date.month, admitted_date__year=month_date.year).count())
        appointment_counts.insert(0, Appointment.objects.filter(date__month=month_date.month, date__year=month_date.year).count())
        revenue_data.insert(0, float(Invoice.objects.filter(created_at__month=month_date.month, created_at__year=month_date.year, status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0))
    
    # Doctor statistics
    doctor_stats = Doctor.objects.annotate(
        appointment_count=Count('appointments'),
        patient_count=Count('appointments__patient', distinct=True)
    ).values('first_name', 'last_name', 'specialty', 'appointment_count', 'patient_count')
    
    # Room statistics
    room_stats = Room.objects.annotate(bed_count=Count('beds')).values('room_type', 'bed_count', 'is_occupied')
    
    context = {
        'months': months,
        'patient_counts': patient_counts,
        'appointment_counts': appointment_counts,
        'revenue_data': revenue_data,
        'doctor_stats': doctor_stats,
        'room_stats': room_stats,
        'total_revenue': float(Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
        'total_pending': float(Invoice.objects.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
        'user_role': user_role,
    }
    return render(request, 'hospital/reports.html', context)

# Charts API
def chart_data(request):
    today = timezone.now()
    
    # Appointment status distribution
    appointment_status = Appointment.objects.values('status').annotate(count=Count('status'))
    
    # Bed status distribution
    bed_status = Bed.objects.values('status').annotate(count=Count('status'))
    
    # Lab test types distribution
    lab_types = LabTest.objects.values('test_type').annotate(count=Count('test_type'))
    
    # Revenue by month
    months = []
    revenue = []
    for i in range(6):
        month_date = today - timedelta(days=30*i)
        months.insert(0, month_date.strftime('%b'))
        revenue.insert(0, float(Invoice.objects.filter(
            created_at__month=month_date.month,
            created_at__year=month_date.year,
            status='paid'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0))
    
    data = {
        'appointment_status': list(appointment_status),
        'bed_status': list(bed_status),
        'lab_types': list(lab_types),
        'months': months,
        'revenue': revenue,
    }
    return JsonResponse(data)

# Notifications
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'hospital/notification_list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notification_list')

# Google Maps
@login_required
def patient_map(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    patients = Patient.objects.exclude(latitude=None, longitude=None)
    return render(request, 'hospital/patient_map.html', {'patients': patients, 'user_role': user_role})

# Patient Portal
@login_required
def patient_portal(request):
    user_role = get_user_role(request.user)
    if user_role != 'patient':
        messages.error(request, 'Access denied - Patient portal only')
        return redirect('home')
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, 'No patient record found')
        return redirect('home')
    
    appointments = patient.appointments.select_related('doctor').order_by('-date')[:5]
    treatments = patient.treatments.select_related('doctor').order_by('-created_at')[:5]
    lab_tests = patient.lab_tests.order_by('-created_at')[:5]
    invoices = patient.invoices.order_by('-created_at')[:5]
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'treatments': treatments,
        'lab_tests': lab_tests,
        'invoices': invoices,
        'notifications': notifications,
        'user_role': user_role,
    }
    return render(request, 'hospital/patient_portal.html', context)

# Doctor Portal
@login_required
def doctor_portal(request):
    user_role = get_user_role(request.user)
    if user_role != 'doctor':
        messages.error(request, 'Access denied - Doctor portal only')
        return redirect('home')
    
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.error(request, 'No doctor record found')
        return redirect('home')
    
    today = timezone.now().date()
    today_appointments = doctor.appointments.filter(date=today).select_related('patient')
    upcoming_appointments = doctor.appointments.filter(date__gt=today).select_related('patient').order_by('date')[:5]
    recent_operations = doctor.operations.select_related('patient').order_by('-created_at')[:5]
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_operations': recent_operations,
        'notifications': notifications,
        'user_role': user_role,
    }
    return render(request, 'hospital/doctor_portal.html', context)

# Staff Views
@login_required
def staff_list(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    staff = Staff.objects.all()
    return render(request, 'hospital/staff_list.html', {'staff': staff, 'user_role': user_role})

@login_required
def add_staff(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        Staff.objects.create(
            name=request.POST['name'],
            staff_type=request.POST['staff_type'],
            gender=request.POST['gender'],
            age=to_int(request.POST.get('age'), 25),
            phone=request.POST['phone'],
            email=request.POST.get('email', ''),
            address=request.POST['address'],
            salary=to_decimal(request.POST.get('salary'), 0),
            shift=request.POST.get('shift', 'morning')
)
        messages.success(request, 'Staff added successfully!')
        return redirect('staff_list')
    return render(request, 'hospital/add_staff.html', {'user_role': user_role})

# ============== NEW FEATURES VIEWS ==============

# Medical Records Views
@login_required
def medical_record_list(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('home')
    records = MedicalRecord.objects.select_related('patient', 'doctor').order_by('-record_date')
    return render(request, 'hospital/medical_record_list.html', {'records': records, 'user_role': user_role})

@login_required
def add_medical_record(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        doctor = get_object_or_404(Doctor, pk=request.POST['doctor'])
        MedicalRecord.objects.create(
            patient=patient,
            doctor=doctor,
            record_type=request.POST['record_type'],
            diagnosis=request.POST['diagnosis'],
            treatment=request.POST.get('treatment', ''),
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Medical record added successfully!')
        return redirect('medical_record_list')
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    return render(request, 'hospital/add_medical_record.html', {'patients': patients, 'doctors': doctors, 'user_role': user_role})


# Allergy Views
@login_required
def allergy_list(request):
    user_role = get_user_role(request.user)
    allergies = Allergy.objects.select_related('patient').order_by('-created_at')
    return render(request, 'hospital/allergy_list.html', {'allergies': allergies, 'user_role': user_role})

@login_required
def allergy_detail(request, pk):
    allergy = get_object_or_404(Allergy, pk=pk)
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('allergy_list')
    return render(request, 'hospital/allergy_detail.html', {'allergy': allergy, 'user_role': user_role})

@login_required
def allergy_edit(request, pk):
    allergy = get_object_or_404(Allergy, pk=pk)
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('allergy_list')
    if request.method == 'POST':
        allergy.allergen = request.POST['allergen']
        allergy.allergy_type = request.POST['allergy_type']
        allergy.severity = request.POST['severity']
        allergy.reactions = request.POST.get('reactions', '')
        allergy.notes = request.POST.get('treatment_notes', '')
        allergy.save()
        messages.success(request, 'Allergy updated successfully!')
        return redirect('allergy_list')
    patients = Patient.objects.all()
    return render(request, 'hospital/allergy_form.html', {'allergy': allergy, 'patients': patients})

@login_required
def allergy_delete(request, pk):
    allergy = get_object_or_404(Allergy, pk=pk)
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('allergy_list')
    if request.method == 'POST':
        allergy.delete()
        messages.success(request, 'Allergy deleted successfully!')
        return redirect('allergy_list')
    return render(request, 'hospital/confirm_delete.html', {'object': allergy, 'url': 'allergy_delete'})

@login_required
def add_allergy(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        Allergy.objects.create(
            patient=patient,
            allergen=request.POST['allergen'],
            allergy_type=request.POST['allergy_type'],
            severity=request.POST['severity'],
            reactions=request.POST.get('reactions', ''),
            discovered_date=request.POST.get('discovered_date', timezone.now().date()),
            notes=request.POST.get('treatment_notes', '')
        )
        messages.success(request, 'Allergy added successfully!')
        return redirect('allergy_list')
    patients = Patient.objects.all()
    return render(request, 'hospital/add_allergy.html', {'patients': patients, 'user_role': user_role})


# Vital Signs Views
@login_required
def vital_sign_list(request):
    user_role = get_user_role(request.user)
    vitals = VitalSign.objects.select_related('patient').order_by('-recorded_at')[:50]
    return render(request, 'hospital/vital_sign_list.html', {'vitals': vitals, 'user_role': user_role})

@login_required
def add_vital_sign(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor', 'nurse']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        VitalSign.objects.create(
            patient=patient,
            blood_pressure_systolic=to_int(request.POST.get('blood_pressure_systolic')),
            blood_pressure_diastolic=to_int(request.POST.get('blood_pressure_diastolic')),
            heart_rate=to_int(request.POST.get('heart_rate')),
            temperature=to_decimal(request.POST.get('temperature')),
            respiratory_rate=to_int(request.POST.get('respiratory_rate')),
            oxygen_saturation=to_int(request.POST.get('oxygen_saturation')),
            weight=to_decimal(request.POST.get('weight')),
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Vital signs recorded successfully!')
        return redirect('vital_sign_list')
    patients = Patient.objects.all()
    return render(request, 'hospital/add_vital_sign.html', {'patients': patients, 'user_role': user_role})


# Prescription Views
@login_required
def prescription_list(request):
    user_role = get_user_role(request.user)
    if user_role == 'patient':
        prescriptions = Prescription.objects.filter(patient=request.user.patient)
    else:
        prescriptions = Prescription.objects.select_related('patient', 'doctor').order_by('-prescription_date')
    return render(request, 'hospital/prescription_list.html', {'prescriptions': prescriptions, 'user_role': user_role})

@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    user_role = get_user_role(request.user)
    if user_role == 'patient' and prescription.patient != request.user.patient:
        messages.error(request, 'Access denied')
        return redirect('prescription_list')
    return render(request, 'hospital/prescription_detail.html', {'prescription': prescription})

@login_required
def prescription_edit(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('prescription_list')
    if request.method == 'POST':
        prescription.medicine_name = request.POST['medicine_name']
        prescription.dosage = request.POST['dosage']
        prescription.frequency = request.POST['frequency']
        prescription.duration = request.POST.get('duration', '')
        prescription.instructions = request.POST.get('instructions', '')
        prescription.start_date = request.POST.get('start_date')
        prescription.save()
        messages.success(request, 'Prescription updated!')
        return redirect('prescription_list')
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    return render(request, 'hospital/prescription_form.html', {'prescription': prescription, 'patients': patients, 'doctors': doctors})

@login_required
def prescription_delete(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('prescription_list')
    if request.method == 'POST':
        prescription.delete()
        messages.success(request, 'Prescription deleted!')
        return redirect('prescription_list')
    return render(request, 'hospital/confirm_delete.html', {'object': prescription, 'url': 'prescription_delete'})

@login_required
def add_prescription(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        doctor = get_object_or_404(Doctor, pk=request.POST['doctor'])
        Prescription.objects.create(
            patient=patient,
            doctor=doctor,
            medicine_name=request.POST['medicine_name'],
            dosage=request.POST['dosage'],
            frequency=request.POST['frequency'],
            duration=request.POST.get('duration', ''),
            instructions=request.POST.get('instructions', ''),
            start_date=request.POST.get('start_date', timezone.now().date())
        )
        messages.success(request, 'Prescription added successfully!')
        return redirect('prescription_list')
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    return render(request, 'hospital/add_prescription.html', {'patients': patients, 'doctors': doctors, 'user_role': user_role})


# Pharmacy Views
@login_required
def medicine_list(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('home')
    medicines = Medicine.objects.select_related('category').order_by('name')
    return render(request, 'hospital/medicine_list.html', {'medicines': medicines, 'user_role': user_role})

@login_required
def add_medicine(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        category = get_object_or_404(MedicineCategory, pk=request.POST['category']) if request.POST.get('category') else None
        Medicine.objects.create(
            name=request.POST['name'],
            generic_name=request.POST.get('generic_name', ''),
            category=category,
            quantity_in_stock=to_int(request.POST.get('quantity_in_stock')),
            unit=request.POST['unit'],
            cost_per_unit=to_decimal(request.POST.get('cost_per_unit')),
            selling_price_per_unit=to_decimal(request.POST.get('selling_price_per_unit')),
            expiry_date=request.POST.get('expiry_date'),
            manufacturer=request.POST.get('manufacturer', ''),
            is_active=True
        )
        messages.success(request, 'Medicine added successfully!')
        return redirect('medicine_list')
    categories = MedicineCategory.objects.all()
    return render(request, 'hospital/add_medicine.html', {'categories': categories, 'user_role': user_role})

@login_required
def pharmacy_order_list(request):
    user_role = get_user_role(request.user)
    if user_role == 'patient':
        orders = PharmacyOrder.objects.filter(patient=request.user.patient)
    else:
        orders = PharmacyOrder.objects.select_related('patient', 'medicine').order_by('-order_date')
    return render(request, 'hospital/pharmacy_order_list.html', {'orders': orders, 'user_role': user_role})

@login_required
def add_pharmacy_order(request):
    user_role = get_user_role(request.user)
    if user_role == 'patient':
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        medicine = get_object_or_404(Medicine, pk=request.POST['medicine'])
        quantity = to_int(request.POST['quantity'])
        PharmacyOrder.objects.create(
            order_number=f"RX{timezone.now().strftime('%Y%m%d%H%M%S')}",
            patient=patient,
            medicine=medicine,
            quantity=quantity,
            status='pending'
        )
        messages.success(request, 'Pharmacy order created successfully!')
        return redirect('pharmacy_order_list')
    patients = Patient.objects.all()
    medicines = Medicine.objects.filter(is_active=True)
    return render(request, 'hospital/add_pharmacy_order.html', {'patients': patients, 'medicines': medicines, 'user_role': user_role})


# Emergency Views
@login_required
def ambulance_list(request):
    user_role = get_user_role(request.user)
    ambulances = Ambulance.objects.filter(is_active=True)
    return render(request, 'hospital/ambulance_list.html', {'ambulances': ambulances, 'user_role': user_role})

@login_required
def add_ambulance(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        Ambulance.objects.create(
            vehicle_number=request.POST['vehicle_number'],
            driver_name=request.POST['driver_name'],
            driver_phone=request.POST['driver_phone'],
            vehicle_type=request.POST.get('vehicle_type', '_basic'),
            is_active=True
        )
        messages.success(request, 'Ambulance added successfully!')
        return redirect('ambulance_list')
    return render(request, 'hospital/add_ambulance.html', {'user_role': user_role})

@login_required
def emergency_admission_list(request):
    user_role = get_user_role(request.user)
    admissions = EmergencyAdmission.objects.select_related('patient').order_by('-admission_time')
    return render(request, 'hospital/emergency_admission_list.html', {'admissions': admissions, 'user_role': user_role})

@login_required
def add_emergency_admission(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        EmergencyAdmission.objects.create(
            patient=patient,
            priority=request.POST['priority'],
            reason=request.POST['reason'],
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Emergency admission added successfully!')
        return redirect('emergency_admission_list')
    patients = Patient.objects.all()
    return render(request, 'hospital/add_emergency_admission.html', {'patients': patients, 'user_role': user_role})


# Insurance Views
@login_required
def insurance_provider_list(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    providers = InsuranceProvider.objects.filter(is_active=True)
    return render(request, 'hospital/insurance_provider_list.html', {'providers': providers, 'user_role': user_role})

@login_required
def add_insurance_provider(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        InsuranceProvider.objects.create(
            name=request.POST['name'],
            code=request.POST['code'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            address=request.POST.get('address', ''),
            is_active=True
        )
        messages.success(request, 'Insurance provider added successfully!')
        return redirect('insurance_provider_list')
    return render(request, 'hospital/add_insurance_provider.html', {'user_role': user_role})

@login_required
def insurance_policy_list(request):
    user_role = get_user_role(request.user)
    if user_role == 'patient':
        policies = InsurancePolicy.objects.filter(patient=request.user.patient)
    else:
        policies = InsurancePolicy.objects.select_related('patient', 'provider').order_by('-start_date')
    return render(request, 'hospital/insurance_policy_list.html', {'policies': policies, 'user_role': user_role})

@login_required
def add_insurance_policy(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        provider = get_object_or_404(InsuranceProvider, pk=request.POST['provider'])
        InsurancePolicy.objects.create(
            patient=patient,
            provider=provider,
            policy_number=request.POST['policy_number'],
            coverage_type=request.POST['coverage_type'],
            coverage_amount=to_decimal(request.POST['coverage_amount']),
            premium_amount=to_decimal(request.POST.get('premium_amount')),
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            is_active=True
        )
        messages.success(request, 'Insurance policy added successfully!')
        return redirect('insurance_policy_list')
    patients = Patient.objects.all()
    providers = InsuranceProvider.objects.filter(is_active=True)
    return render(request, 'hospital/add_insurance_policy.html', {'patients': patients, 'providers': providers, 'user_role': user_role})

@login_required
def insurance_claim_list(request):
    user_role = get_user_role(request.user)
    if user_role == 'patient':
        claims = InsuranceClaim.objects.filter(patient=request.user.patient)
    else:
        claims = InsuranceClaim.objects.select_related('patient', 'policy').order_by('-claim_date')
    return render(request, 'hospital/insurance_claim_list.html', {'claims': claims, 'user_role': user_role})

@login_required
def add_insurance_claim(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        policy = get_object_or_404(InsurancePolicy, pk=request.POST['policy'])
        InsuranceClaim.objects.create(
            claim_number=f"CLM{timezone.now().strftime('%Y%m%d%H%M%S')}",
            patient=patient,
            policy=policy,
            claim_amount=to_decimal(request.POST['claim_amount']),
            description=request.POST.get('description', ''),
            status='pending'
        )
        messages.success(request, 'Insurance claim created successfully!')
        return redirect('insurance_claim_list')
    patients = Patient.objects.all()
    return render(request, 'hospital/add_insurance_claim.html', {'patients': patients, 'user_role': user_role})

@login_required
def payment_plan_list(request):
    user_role = get_user_role(request.user)
    if user_role == 'patient':
        payment_plans = PaymentPlan.objects.filter(patient=request.user.patient)
    else:
        payment_plans = PaymentPlan.objects.select_related('patient', 'invoice').order_by('-created_at')
    return render(request, 'hospital/payment_plan_list.html', {'payment_plans': payment_plans, 'user_role': user_role})

@login_required
def add_payment_plan(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        invoice = get_object_or_404(Invoice, pk=request.POST['invoice']) if request.POST.get('invoice') else None
        unpaid_invoices = Invoice.objects.filter(patient=patient, status='pending')
        PaymentPlan.objects.create(
            patient=patient,
            invoice=invoice,
            total_amount=to_decimal(request.POST['total_amount']),
            monthly_payment=to_decimal(request.POST['monthly_payment']),
            next_payment_date=request.POST['next_payment_date'],
            status='active'
        )
        messages.success(request, 'Payment plan created successfully!')
        return redirect('payment_plan_list')
    patients = Patient.objects.all()
    unpaid_invoices = []
    return render(request, 'hospital/add_payment_plan.html', {'patients': patients, 'unpaid_invoices': unpaid_invoices, 'user_role': user_role})

@login_required
def payment_plan_detail(request, pk):
    plan = get_object_or_404(PaymentPlan, pk=pk)
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist'] and plan.patient.user != request.user:
        messages.error(request, 'Access denied')
        return redirect('payment_plan_list')
    return render(request, 'hospital/payment_plan_detail.html', {'plan': plan})

@login_required
def payment_plan_edit(request, pk):
    plan = get_object_or_404(PaymentPlan, pk=pk)
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('payment_plan_list')
    if request.method == 'POST':
        plan.total_amount = to_decimal(request.POST['total_amount'])
        plan.monthly_payment = to_decimal(request.POST['monthly_payment'])
        plan.next_payment_date = request.POST['next_payment_date']
        plan.status = request.POST['status']
        plan.save()
        messages.success(request, 'Payment plan updated!')
        return redirect('payment_plan_list')
    patients = Patient.objects.all()
    return render(request, 'hospital/payment_plan_form.html', {'plan': plan, 'patients': patients})

@login_required
def payment_plan_delete(request, pk):
    plan = get_object_or_404(PaymentPlan, pk=pk)
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'receptionist']:
        messages.error(request, 'Access denied')
        return redirect('payment_plan_list')
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Payment plan deleted!')
        return redirect('payment_plan_list')
    return render(request, 'hospital/confirm_delete.html', {'object': plan, 'url': 'payment_plan_delete'})


# Audit Log Views
@login_required
def audit_log_list(request):
    user_role = get_user_role(request.user)
    if user_role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('home')
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:100]
    return render(request, 'hospital/audit_log_list.html', {'logs': logs, 'user_role': user_role})


# Document Views
@login_required
def document_list(request):
    user_role = get_user_role(request.user)
    if user_role == 'patient':
        documents = Document.objects.filter(patient=request.user.patient)
    else:
        documents = Document.objects.select_related('patient', 'uploaded_by').order_by('-uploaded_at')
    return render(request, 'hospital/document_list.html', {'documents': documents, 'user_role': user_role})

@login_required
def add_document(request):
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'doctor']:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=request.POST['patient'])
        Document.objects.create(
            patient=patient,
            title=request.POST['title'],
            document_type=request.POST['document_type'],
            description=request.POST.get('description', ''),
            uploaded_by=request.user
        )
        messages.success(request, 'Document added successfully!')
        return redirect('document_list')
    patients = Patient.objects.all()
    return render(request, 'hospital/add_document.html', {'patients': patients, 'user_role': user_role})
