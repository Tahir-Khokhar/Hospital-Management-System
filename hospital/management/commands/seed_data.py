from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hospital.models import (Profile, Doctor, Patient, Room, Bed, Appointment,
                             Operation, Treatment, LabTest, Invoice, Notification, Staff,
                             MedicalRecord, Allergy, VitalSign, Prescription, MedicineCategory,
                             Medicine, PharmacyOrder, EmergencyContact, Ambulance, EmergencyAdmission,
                             InsuranceProvider, InsurancePolicy, InsuranceClaim, PaymentPlan,
                             AuditLog, Document)
from django.utils import timezone
import random
from datetime import datetime, timedelta, date, time
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed database with 500+ comprehensive demo records for all features'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Clearing old data...'))
        # Clear in correct order to avoid foreign key constraints
        Notification.objects.all().delete()
        AuditLog.objects.all().delete()
        Document.objects.all().delete()
        InsuranceClaim.objects.all().delete()
        InsurancePolicy.objects.all().delete()
        PaymentPlan.objects.all().delete()
        PharmacyOrder.objects.all().delete()
        EmergencyContact.objects.all().delete()
        EmergencyAdmission.objects.all().delete()
        Ambulance.objects.all().delete()
        Invoice.objects.all().delete()
        LabTest.objects.all().delete()
        Treatment.objects.all().delete()
        Operation.objects.all().delete()
        Appointment.objects.all().delete()
        VitalSign.objects.all().delete()
        Prescription.objects.all().delete()
        Allergy.objects.all().delete()
        MedicalRecord.objects.all().delete()
        Bed.objects.all().delete()
        Room.objects.all().delete()
        Staff.objects.all().delete()
        Medicine.objects.all().delete()
        MedicineCategory.objects.all().delete()
        Doctor.objects.all().delete()
        Patient.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS('Starting comprehensive data seeding...\n'))
        
        # Common data
        specialties = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Dermatology', 
                      'Oncology', 'Radiology', 'General Surgery', 'Internal Medicine', 'Psychiatry',
                      'Emergency Medicine', 'Anesthesiology']
        genders = ['Male', 'Female']
        first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
                      'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
                      'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
                      'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Steven', 'Ashley',
                      'Paul', 'Dorothy', 'Andrew', 'Kimberly', 'Joshua', 'Donna', 'Kenneth', 'Emily']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                     'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
                     'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker']
        
        # 1. Create Users and Profiles
        self.stdout.write('Creating users and profiles...')
        
        # Admin user
        admin_user, _ = User.objects.get_or_create(username='admin')
        admin_user.set_password('admin123')
        admin_user.email = 'admin@hospital.com'
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'User'
        admin_user.save()
        Profile.objects.get_or_create(user=admin_user, defaults={'role': 'admin', 'phone': '+1-555-0100'})
        
        # Doctor users
        doctors_list = []
        for i in range(25):
            user, _ = User.objects.get_or_create(username=f'doctor{i}')
            user.set_password('doctor123')
            user.email = f'doctor{i}@hospital.com'
            user.first_name = random.choice(first_names)
            user.last_name = random.choice(last_names)
            user.save()
            Profile.objects.get_or_create(user=user, defaults={'role': 'doctor', 'phone': f'+1-555-{random.randint(1000,9999)}'})
            
            doctor = Doctor.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                gender=random.choice(genders),
                specialty=random.choice(specialties),
                experience_years=random.randint(1, 35),
                phone=f'+1-555-{random.randint(1000,9999)}',
                email=f'doctor{i}@hospital.com',
                bio=f'Experienced {random.choice(specialties).lower()} specialist.',
                is_available=random.choice([True, True, True, False])
            )
            doctors_list.append(doctor)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 25 doctors'))
        
        # Patient users
        patients_list = []
        for i in range(80):
            user = None
            if i < 40:  # Half have user accounts
                user, _ = User.objects.get_or_create(username=f'patient{i}')
                user.set_password('patient123')
                user.email = f'patient{i}@hospital.com'
                user.first_name = random.choice(first_names)
                user.last_name = random.choice(last_names)
                user.save()
                Profile.objects.get_or_create(user=user, defaults={'role': 'patient', 'phone': f'+1-555-{random.randint(1000,9999)}'})
            
            patient = Patient.objects.create(
                user=user,
                first_name=user.first_name if user else random.choice(first_names),
                last_name=user.last_name if user else random.choice(last_names),
                age=random.randint(5, 90),
                gender=random.choice(genders + ['Other']),
                phone=f'+1-555-{random.randint(1000,9999)}',
                address=f'{random.randint(100,9999)} {random.choice(["Main St", "Oak Ave", "Park Rd", "Elm St", "Cedar Ln"])}',
                latitude=round(random.uniform(33.7, 34.1), 6),
                longitude=round(random.uniform(-118.5, -118.1), 6),
                medical_history=random.choice(['No significant history', 'Diabetes Type 2', 'Hypertension', 'Asthma', 'None'])
            )
            patients_list.append(patient)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 80 patients'))
        
        # 2. Staff Members
        staff_list = []
        staff_types_list = ['nurse', 'wardboy', 'receptionist', 'technician']
        for i in range(40):
            staff = Staff.objects.create(
                name=f'{random.choice(first_names)} {random.choice(last_names)}',
                staff_type=random.choice(staff_types_list),
                gender=random.choice(genders),
                age=random.randint(22, 60),
                phone=f'+1-555-{random.randint(1000,9999)}',
                email=f'staff{i}@hospital.com',
                address=f'{random.randint(100,9999)} Staff Avenue',
                salary=round(random.uniform(35000, 85000), 2),
                is_active=True,
                shift=random.choice(['morning', 'evening', 'night'])
            )
            staff_list.append(staff)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 40 staff members'))
        
        # 3. Medicine Categories and Medicines
        self.stdout.write('Creating pharmacy inventory...')
        categories = ['Antibiotics', 'Pain Relief', 'Antihistamines', 'Antacids', 'Vitamins', 
                     'Cardiovascular', 'Diabetes', 'Respiratory', 'Antidepressants', 'Antiviral']
        med_categories = []
        for cat_name in categories:
            cat, _ = MedicineCategory.objects.get_or_create(name=cat_name)
            med_categories.append(cat)
        
        medicine_data = [
            ('Paracetamol 500mg', 'Antibiotics', 'tablets'),
            ('Amoxicillin 250mg', 'Antibiotics', 'capsules'),
            ('Ibuprofen 400mg', 'Pain Relief', 'tablets'),
            ('Aspirin 100mg', 'Pain Relief', 'tablets'),
            ('Cetirizine 10mg', 'Antihistamines', 'tablets'),
            ('Omeprazole 20mg', 'Antacids', 'capsules'),
            ('Amlodipine 5mg', 'Cardiovascular', 'tablets'),
            ('Metformin 500mg', 'Diabetes', 'tablets'),
            ('Salbutamol Inhaler', 'Respiratory', 'inhaler'),
            ('Vitamin D3 1000IU', 'Vitamins', 'tablets'),
        ]
        
        medicines_list = []
        for med_name, cat_name, unit in medicine_data:
            for j in range(5):  # Create 5 batches of each
                category = MedicineCategory.objects.get(name=cat_name)
                med = Medicine.objects.create(
                    name=f'{med_name} (Batch {j+1})',
                    generic_name=med_name.split()[0],
                    category=category,
                    quantity_in_stock=random.randint(50, 500),
                    unit=unit,
                    reorder_level=20,
                    cost_per_unit=round(random.uniform(0.5, 5.0), 2),
                    selling_price_per_unit=round(random.uniform(1.0, 15.0), 2),
                    manufacturer=f'PharmaCo {random.randint(1, 10)}',
                    expiry_date=date.today() + timedelta(days=random.randint(180, 1095)),
                    is_active=True
                )
                medicines_list.append(med)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(med_categories)} categories and {len(medicines_list)} medicines'))
        
        # 4. Rooms and Beds
        self.stdout.write('Creating rooms and beds...')
        room_types_list = ['general', 'private', 'icu', 'semi_private', 'deluxe', 'operation']
        rooms_list = []
        total_beds = 0
        
        for i in range(30):
            capacity = random.randint(1, 4)
            room = Room.objects.create(
                room_number=f'{100+i}',
                room_type=random.choice(room_types_list),
                floor=random.randint(1, 5),
                capacity=capacity,
                is_occupied=random.choice([True, False, False, False]),
                price_per_day=round(random.uniform(100, 800), 2)
            )
            rooms_list.append(room)
            
            for j in range(1, capacity + 1):
                Bed.objects.create(
                    bed_number=f'{room.room_number}-{j}',
                    room=room,
                    status=random.choice(['available', 'available', 'occupied', 'maintenance']),
                    patient=random.choice(patients_list) if random.random() > 0.6 else None
                )
                total_beds += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 30 rooms with {total_beds} beds'))
        
        # 5. Appointments
        self.stdout.write('Creating appointments...')
        appointments_list = []
        appointment_statuses = ['Scheduled', 'Completed', 'Cancelled', 'No-Show']
        
        for i in range(100):
            apt_date = date.today() + timedelta(days=random.randint(-60, 60))
            apt = Appointment.objects.create(
                patient=random.choice(patients_list),
                doctor=random.choice(doctors_list),
                date=apt_date,
                time=time(random.randint(8, 17), random.choice([0, 15, 30, 45])),
                status=random.choice(appointment_statuses),
                notes=random.choice(['Routine checkup', 'Follow-up visit', 'Initial consultation', 'Emergency visit'])
            )
            appointments_list.append(apt)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 100 appointments'))
        
        # 6. Operations
        self.stdout.write('Creating operations...')
        operation_names = ['Appendectomy', 'Knee Replacement', 'Heart Bypass', 'Cataract Surgery',
                          'Hernia Repair', 'Gallbladder Removal', 'Hip Replacement', 'Spinal Fusion',
                          'Coronary Angioplasty', 'Tonsillectomy', 'Cesarean Section', 'Fracture Repair']
        
        for i in range(40):
            Operation.objects.create(
                patient=random.choice(patients_list),
                doctor=random.choice(doctors_list),
                room=random.choice(rooms_list) if random.random() > 0.3 else None,
                operation_name=random.choice(operation_names),
                description='Standard surgical procedure',
                scheduled_date=timezone.now() + timedelta(days=random.randint(-30, 90)),
                duration_hours=random.randint(1, 6),
                status=random.choice(['scheduled', 'completed', 'cancelled', 'in_progress']),
                cost=round(random.uniform(2000, 25000), 2)
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 40 operations'))
        
        # 7. Treatments
        self.stdout.write('Creating treatments...')
        treatment_names = ['Physical Therapy', 'Chemotherapy', 'Antibiotic Therapy', 'Pain Management',
                          'Radiation Therapy', 'Dialysis', 'Insulin Therapy', 'Respiratory Therapy',
                          'Wound Care', 'Cardiac Rehabilitation']
        
        for i in range(50):
            Treatment.objects.create(
                patient=random.choice(patients_list),
                doctor=random.choice(doctors_list),
                treatment_name=random.choice(treatment_names),
                description='Comprehensive treatment plan',
                start_date=date.today() - timedelta(days=random.randint(0, 90)),
                end_date=date.today() + timedelta(days=random.randint(0, 90)) if random.random() > 0.3 else None,
                medications='Prescribed medications as needed',
                instructions='Follow up regularly',
                cost=round(random.uniform(200, 5000), 2)
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 50 treatments'))
        
        # 8. Lab Tests
        self.stdout.write('Creating lab tests...')
        test_types_list = ['Blood Test', 'Urine Test', 'X-Ray', 'MRI', 'CT Scan', 'Ultrasound', 'ECG', 'Blood Culture']
        
        for i in range(60):
            LabTest.objects.create(
                patient=random.choice(patients_list),
                test_type=random.choice(test_types_list),
                description='Diagnostic laboratory test',
                status=random.choice(['pending', 'in_progress', 'completed', 'cancelled']),
                result='Results within normal range' if random.random() > 0.3 else 'Abnormal findings detected',
                cost=round(random.uniform(50, 800), 2),
                scheduled_date=date.today() + timedelta(days=random.randint(-30, 30)),
                completed_date=date.today() if random.random() > 0.4 else None
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 60 lab tests'))
        
        # 9. Invoices
        self.stdout.write('Creating invoices and billing...')
        invoice_statuses = ['pending', 'paid', 'overdue', 'cancelled']
        invoices_list = []
        
        for i in range(70):
            inv = Invoice.objects.create(
                invoice_number=f'INV-{20260000+i}',
                patient=random.choice(patients_list),
                appointment=random.choice(appointments_list) if random.random() > 0.5 else None,
                room_charges=round(random.uniform(0, 2000), 2),
                medication_charges=round(random.uniform(0, 500), 2),
                other_charges=round(random.uniform(0, 300), 2),
                status=random.choice(invoice_statuses),
                due_date=date.today() + timedelta(days=random.randint(-10, 60)),
                paid_date=date.today() if random.random() > 0.5 else None,
                notes='Payment due by specified date'
            )
            inv.total_amount = inv.calculate_total()
            inv.save()
            invoices_list.append(inv)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 70 invoices'))
        
        # 10. Medical Records
        self.stdout.write('Creating medical records...')
        record_types_list = ['diagnosis', 'consultation', 'followup', 'emergency', 'routine']
        diagnoses_list = [
            'Type 2 Diabetes Mellitus', 'Hypertension Stage 2', 'Osteoarthritis',
            'Asthma - Moderate', 'Migraine with Aura', 'Chronic Back Pain',
            'Acute Bronchitis', 'GERD', 'Anxiety Disorder', 'Depression',
            'Hyperthyroidism', 'Anemia', 'Pneumonia', 'Urinary Tract Infection'
        ]
        
        for i in range(45):
            MedicalRecord.objects.create(
                patient=random.choice(patients_list),
                doctor=random.choice(doctors_list),
                record_type=random.choice(record_types_list),
                diagnosis=random.choice(diagnoses_list),
                symptoms=random.choice(['Fever, cough, fatigue', 'Chest pain, dizziness', 'Joint pain, swelling',
                                       'Headache, nausea', 'Shortness of breath']),
                findings='Physical examination conducted',
                notes='Treatment plan prescribed',
                follow_up_date=date.today() + timedelta(days=random.randint(7, 60))
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 45 medical records'))
        
        # 11. Allergies
        self.stdout.write('Creating allergy records...')
        allergens_list = [
            ('Penicillin', 'drug', 'severe'), ('Peanuts', 'food', 'life_threatening'),
            ('Latex', 'contact', 'moderate'), ('Dust Mites', 'environmental', 'mild'),
            ('Shellfish', 'food', 'severe'), ('Bee Stings', 'environmental', 'life_threatening'),
            ('Aspirin', 'drug', 'moderate'), ('Pollen', 'environmental', 'mild')
        ]
        
        for i in range(30):
            allergen, allergy_type, severity = random.choice(allergens_list)
            Allergy.objects.create(
                patient=random.choice(patients_list),
                allergen=allergen,
                allergy_type=allergy_type,
                severity=severity,
                reactions='Skin rash, swelling, breathing difficulty',
                discovered_date=date.today() - timedelta(days=random.randint(30, 1000))
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 30 allergy records'))
        
        # 12. Vital Signs
        self.stdout.write('Creating vital signs records...')
        for i in range(50):
            VitalSign.objects.create(
                patient=random.choice(patients_list),
                recorded_by=random.choice(doctors_list),
                blood_pressure_systolic=random.randint(100, 160),
                blood_pressure_diastolic=random.randint(60, 100),
                heart_rate=random.randint(55, 110),
                temperature=round(random.uniform(36.1, 38.5), 1),
                respiratory_rate=random.randint(12, 24),
                oxygen_saturation=random.randint(92, 100),
                weight=round(random.uniform(45, 120), 1),
                height=round(random.uniform(150, 190), 1),
                notes='Routine vital signs check'
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 50 vital signs records'))
        
        # 13. Prescriptions
        self.stdout.write('Creating prescriptions...')
        for i in range(60):
            Prescription.objects.create(
                patient=random.choice(patients_list),
                doctor=random.choice(doctors_list),
                medicine_name=random.choice([m.name for m in medicines_list[:10]]),
                dosage=f'{random.choice(["1", "2"])} tablet(s)',
                frequency=random.choice(['Once daily', 'Twice daily', 'Three times daily', 'As needed']),
                duration=f'{random.choice([7, 10, 14, 21, 30])} days',
                instructions='Take with food and water',
                start_date=date.today() - timedelta(days=random.randint(0, 60))
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 60 prescriptions'))
        
        # 14. Ambulances
        self.stdout.write('Creating ambulance fleet...')
        ambulance_data = [
            ('AMB-001', 'John Smith', '+1-555-1001', 'basic'),
            ('AMB-002', 'Mike Johnson', '+1-555-1002', 'advanced'),
            ('AMB-003', 'Robert Williams', '+1-555-1003', 'icu'),
            ('AMB-004', 'David Brown', '+1-555-1004', 'basic'),
            ('AMB-005', 'James Davis', '+1-555-1005', 'advanced'),
            ('AMB-006', 'William Miller', '+1-555-1006', 'basic'),
            ('AMB-007', 'Richard Wilson', '+1-555-1007', 'icu'),
            ('AMB-008', 'Thomas Moore', '+1-555-1008', 'advanced'),
            ('AMB-009', 'Charles Taylor', '+1-555-1009', 'basic'),
            ('AMB-010', 'Daniel Anderson', '+1-555-1010', 'icu'),
        ]
        
        for vehicle_num, driver, phone, vtype in ambulance_data:
            Ambulance.objects.create(
                vehicle_number=vehicle_num,
                driver_name=driver,
                driver_phone=phone,
                current_location=f'Hospital Bay {random.randint(1, 5)}',
                status=random.choice(['available', 'available', 'dispatched', 'returning', 'maintenance']),
                is_active=True
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 10 ambulances'))
        
        # 15. Emergency Admissions
        self.stdout.write('Creating emergency admissions...')
        priorities_list = ['critical', 'urgent', 'stable']
        emergency_reasons = [
            'Severe chest pain - possible heart attack',
            'Multiple fractures from car accident',
            'Severe allergic reaction - anaphylaxis',
            'Stroke symptoms - right side weakness',
            'Severe abdominal pain - appendicitis suspected',
            'Respiratory distress - severe asthma attack',
            'Head trauma - loss of consciousness',
            'Severe burns - 2nd and 3rd degree',
            'Diabetic emergency - hypoglycemia',
            'Seizure - prolonged convulsions'
        ]
        
        for i in range(20):
            EmergencyAdmission.objects.create(
                patient=random.choice(patients_list),
                priority=random.choice(priorities_list),
                reason=random.choice(emergency_reasons),
                description=f'Emergency admission processed, immediate attention required',
                initial_diagnosis=random.choice(diagnoses_list),
                admission_time=timezone.now() - timedelta(hours=random.randint(1, 168)),
                admitted_to=random.choice(rooms_list) if random.random() > 0.3 else None,
                is_discharged=random.choice([True, False, False])
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 20 emergency admissions'))
        
        # 16. Emergency Contacts
        self.stdout.write('Creating emergency contacts...')
        relationships_list = ['Spouse', 'Parent', 'Sibling', 'Child', 'Friend', 'Guardian']
        
        for i in range(50):
            EmergencyContact.objects.create(
                patient=random.choice(patients_list),
                name=f'{random.choice(first_names)} {random.choice(last_names)}',
                relationship=random.choice(relationships_list),
                phone=f'+1-555-{random.randint(2000, 9999)}',
                email=f'contact{random.randint(1, 200)}@email.com',
                address=f'{random.randint(100, 9999)} Emergency Lane',
                is_primary=random.choice([True, False])
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 50 emergency contacts'))
        
        # 17. Insurance Providers
        self.stdout.write('Creating insurance providers...')
        insurance_providers_data = [
            ('BlueCross BlueShield', 'BCBS', '+1-800-555-0101', 'info@bcbs.com', '123 Insurance Plaza, NY'),
            ('Aetna Health', 'AETNA', '+1-800-555-0102', 'contact@aetna.com', '456 Health Ave, CT'),
            ('UnitedHealth Group', 'UHG', '+1-800-555-0103', 'support@uhg.com', '789 Medical Blvd, MN'),
            ('Cigna Healthcare', 'CIGNA', '+1-800-555-0104', 'help@cigna.com', '321 Wellness St, PA'),
            ('Kaiser Permanente', 'KP', '+1-800-555-0105', 'info@kp.org', '654 Care Dr, CA'),
            ('Humana Inc', 'HUMANA', '+1-800-555-0106', 'service@humana.com', '987 Life Way, KY'),
            ('Centene Corporation', 'CNC', '+1-800-555-0107', 'info@centene.com', '234 Health Plaza, MO'),
            ('Anthem Inc', 'ANTHEM', '+1-800-555-0108', 'support@anthem.com', '567 Medical Center, IN'),
        ]
        
        providers_list = []
        for name, code, phone, email, address in insurance_providers_data:
            provider = InsuranceProvider.objects.create(
                name=name,
                code=code,
                phone=phone,
                email=email,
                address=address,
                is_active=True
            )
            providers_list.append(provider)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 8 insurance providers'))
        
        # 18. Insurance Policies
        self.stdout.write('Creating insurance policies...')
        coverage_types_list = ['individual', 'family', 'group']
        
        for i in range(35):
            provider = random.choice(providers_list)
            InsurancePolicy.objects.create(
                patient=random.choice(patients_list),
                provider=provider,
                policy_number=f'POL-{random.randint(100000, 999999)}',
                holder_name=f'{random.choice(first_names)} {random.choice(last_names)}',
                holder_relationship=random.choice(relationships_list),
                coverage_type=random.choice(coverage_types_list),
                coverage_amount=round(random.uniform(50000, 1000000), 2),
                start_date=date.today() - timedelta(days=random.randint(0, 730)),
                end_date=date.today() + timedelta(days=random.randint(30, 730)),
                is_active=True,
                notes='Active insurance policy'
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 35 insurance policies'))
        
        # 19. Insurance Claims
        self.stdout.write('Creating insurance claims...')
        claim_statuses_list = ['submitted', 'under_review', 'approved', 'rejected', 'partial', 'paid']
        policies_list = list(InsurancePolicy.objects.all())
        
        for i in range(25):
            if policies_list:
                InsuranceClaim.objects.create(
                    claim_number=f'CLM{timezone.now().strftime("%Y%m%d")}{random.randint(1000, 9999)}',
                    patient=random.choice(patients_list),
                    policy=random.choice(policies_list),
                    invoice=random.choice(invoices_list) if random.random() > 0.5 else None,
                    claim_amount=round(random.uniform(500, 50000), 2),
                    approved_amount=round(random.uniform(500, 40000), 2) if random.random() > 0.3 else None,
                    status=random.choice(claim_statuses_list),
                    claim_date=date.today() - timedelta(days=random.randint(1, 120)),
                    notes='Insurance claim for medical treatment'
                )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 25 insurance claims'))
        
        # 20. Payment Plans
        self.stdout.write('Creating payment plans...')
        for i in range(15):
            if invoices_list:
                inv = random.choice(invoices_list)
                PaymentPlan.objects.create(
                    patient=inv.patient,
                    invoice=inv,
                    total_amount=inv.total_amount,
                    monthly_payment=round(inv.total_amount / random.choice([6, 12, 18, 24]), 2),
                    start_date=date.today(),
                    next_payment_date=date.today() + timedelta(days=30),
                    end_date=date.today() + timedelta(days=random.choice([180, 365, 540, 720])),
                    status=random.choice(['active', 'active', 'completed', 'defaulted']),
                    notes='Installment payment plan'
                )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 15 payment plans'))
        
        # 21. Pharmacy Orders
        self.stdout.write('Creating pharmacy orders...')
        prescriptions_list = list(Prescription.objects.all())
        
        for i in range(20):
            if medicines_list:
                PharmacyOrder.objects.create(
                    order_number=f'RX{timezone.now().strftime("%Y%m%d%H")}{random.randint(100, 999)}',
                    patient=random.choice(patients_list),
                    prescription=random.choice(prescriptions_list) if prescriptions_list else None,
                    medicine=random.choice(medicines_list),
                    quantity=random.randint(1, 60),
                    status=random.choice(['pending', 'approved', 'dispensed', 'cancelled']),
                    ordered_by=random.choice(doctors_list),
                    order_date=timezone.now() - timedelta(days=random.randint(0, 60)),
                    dispensed_date=timezone.now() - timedelta(days=random.randint(0, 30)) if random.random() > 0.5 else None,
                    notes='Pharmacy order for prescribed medication'
                )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 20 pharmacy orders'))
        
        # 22. Documents
        self.stdout.write('Creating documents...')
        doc_types_list = ['report', 'prescription', 'lab_result', 'insurance', 'id_proof', 'other']
        
        for i in range(30):
            Document.objects.create(
                patient=random.choice(patients_list),
                title=f'{random.choice(doc_types_list).replace("_", " ").title()} - Patient Record',
                document_type=random.choice(doc_types_list),
                description=f'Document uploaded for patient medical records',
                uploaded_by=admin_user,
                uploaded_at=timezone.now() - timedelta(days=random.randint(0, 180))
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 30 documents'))
        
        # 23. Notifications
        self.stdout.write('Creating notifications...')
        all_users = list(User.objects.all())
        notification_types = ['email', 'sms', 'app']
        notification_subjects = [
            'Appointment Reminder', 'Lab Results Ready', 'Payment Due',
            'New Message from Doctor', 'Prescription Ready', 'Emergency Alert',
            'Follow-up Required', 'Test Results Available'
        ]
        
        for i in range(40):
            Notification.objects.create(
                recipient=random.choice(all_users),
                notification_type=random.choice(notification_types),
                subject=random.choice(notification_subjects),
                message='This is an automated notification from Hospital Management System.',
                is_read=random.choice([True, False])
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 40 notifications'))
        
        # Final Summary
        total_records = (
            Patient.objects.count() + Doctor.objects.count() + Staff.objects.count() +
            Room.objects.count() + Bed.objects.count() + Appointment.objects.count() +
            Operation.objects.count() + Treatment.objects.count() + LabTest.objects.count() +
            Invoice.objects.count() + MedicalRecord.objects.count() + Allergy.objects.count() +
            VitalSign.objects.count() + Prescription.objects.count() + MedicineCategory.objects.count() +
            Medicine.objects.count() + PharmacyOrder.objects.count() + EmergencyContact.objects.count() +
            Ambulance.objects.count() + EmergencyAdmission.objects.count() +
            InsuranceProvider.objects.count() + InsurancePolicy.objects.count() +
            InsuranceClaim.objects.count() + PaymentPlan.objects.count() +
            Document.objects.count() + Notification.objects.count()
        )
        
        self.stdout.write('\n' + self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('DATABASE SEEDING COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'\nTotal Records Created: {total_records}+\n'))
        self.stdout.write(self.style.WARNING('DEMO DATA SUMMARY:'))
        self.stdout.write(f'  • Patients: {Patient.objects.count()}')
        self.stdout.write(f'  • Doctors: {Doctor.objects.count()}')
        self.stdout.write(f'  • Staff: {Staff.objects.count()}')
        self.stdout.write(f'  • Rooms: {Room.objects.count()}')
        self.stdout.write(f'  • Beds: {Bed.objects.count()}')
        self.stdout.write(f'  • Appointments: {Appointment.objects.count()}')
        self.stdout.write(f'  • Operations: {Operation.objects.count()}')
        self.stdout.write(f'  • Treatments: {Treatment.objects.count()}')
        self.stdout.write(f'  • Lab Tests: {LabTest.objects.count()}')
        self.stdout.write(f'  • Invoices: {Invoice.objects.count()}')
        self.stdout.write(f'  • Medical Records: {MedicalRecord.objects.count()}')
        self.stdout.write(f'  • Allergies: {Allergy.objects.count()}')
        self.stdout.write(f'  • Vital Signs: {VitalSign.objects.count()}')
        self.stdout.write(f'  • Prescriptions: {Prescription.objects.count()}')
        self.stdout.write(f'  • Medicine Categories: {MedicineCategory.objects.count()}')
        self.stdout.write(f'  • Medicines: {Medicine.objects.count()}')
        self.stdout.write(f'  • Pharmacy Orders: {PharmacyOrder.objects.count()}')
        self.stdout.write(f'  • Emergency Contacts: {EmergencyContact.objects.count()}')
        self.stdout.write(f'  • Ambulances: {Ambulance.objects.count()}')
        self.stdout.write(f'  • Emergency Admissions: {EmergencyAdmission.objects.count()}')
        self.stdout.write(f'  • Insurance Providers: {InsuranceProvider.objects.count()}')
        self.stdout.write(f'  • Insurance Policies: {InsurancePolicy.objects.count()}')
        self.stdout.write(f'  • Insurance Claims: {InsuranceClaim.objects.count()}')
        self.stdout.write(f'  • Payment Plans: {PaymentPlan.objects.count()}')
        self.stdout.write(f'  • Documents: {Document.objects.count()}')
        self.stdout.write(f'  • Notifications: {Notification.objects.count()}')
        self.stdout.write('\n' + self.style.SUCCESS('='*60))
        self.stdout.write(self.style.WARNING('\nLOGIN CREDENTIALS:'))
        self.stdout.write('  Admin: username=admin, password=admin123')
        self.stdout.write('  Doctor: username=doctor0-24, password=doctor123')
        self.stdout.write('  Patient: username=patient0-39, password=patient123')
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

