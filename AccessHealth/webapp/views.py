from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash,logout,login
from django.contrib.auth.models import User
from .forms import *
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
from django.db.models import Q, Count, Avg, Subquery, OuterRef
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
from .models import *
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import View



def doctor_signup_view(request):
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor account created successfully. You can now log in.")
            return redirect('doctor_login') 
    else:
        form = DoctorSignupForm()

    return render(request, 'doctorsignup.html', {'form': form})

def patient_signup_view(request):
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient account created successfully. You can now log in.")
            return redirect('patient_login')
    else:
        form = PatientSignupForm()
    
    return render(request, 'patientsignup.html', {'form': form})

def patient_login_view(request):
    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # 1. Check if user exists (Case Insensitive)
            try:
                user_obj = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                messages.error(request, "Invalid login credentials.")
                return render(request, 'loginpatient.html', {'form': form})
            
            # 2. Authenticate
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                # 3. CRITICAL FIX: Check for 'patient_profile' instead of 'patient'
                if hasattr(user, 'patient_profile'):
                    login(request, user)
                    messages.success(request, "Login successful.")
                    return redirect('patient_dashboard')
                else:
                    # User exists but is likely a Doctor or Admin
                    messages.error(request, "This account is not registered as a patient.")
            else:
                messages.error(request, "Invalid login credentials.")
                
    else:
        form = PatientLoginForm()
        
    return render(request, 'loginpatient.html', {'form': form})



def doctor_login_view(request):
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            # 1. The form validates the email/password and returns the user object
            user = form.get_user()
            
            if user:
                # 2. CRITICAL CHECK: Is this user actually a Doctor?
                if hasattr(user, 'doctor_profile'):
                    login(request, user)
                    
                    # Use the doctor's name if available, otherwise fallback
                    doctor_name = user.last_name if user.last_name else user.username
                    messages.success(request, f'Welcome back, Dr. {doctor_name}!')
                    
                    return redirect('doctor_dashboard')
                else:
                    # User exists (e.g., a Patient), but is NOT a Doctor.
                    # Deny access to the doctor portal.
                    messages.error(request, 'Invalid email or password.')
            else:
                # Password didn't match or user not found
                messages.error(request, 'Invalid email or password.')
                
    else:
        form = DoctorLoginForm()

    return render(request, 'logindoctor.html', {'form': form})


def landing(request): 
 #return HttpResponse("Hello, Django!“)
 return render(request, 'landing_page.html')

# Create your views here.




class DoctorDashboardView(LoginRequiredMixin, View):
    login_url = 'doctor_login'
    redirect_field_name = 'next'
    
    def get(self, request, *args, **kwargs):
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return render(request, 'error.html', {
                'error': 'Doctor profile not found',
                'message': 'Please contact administrator'
            })
        
        today = timezone.now().date()
        
        # ✅ GET NOTIFICATIONS FIRST (before slicing)
        all_notifications = Notification.objects.filter(doctor=doctor).order_by('-created_at')
        unread_count = all_notifications.filter(is_read=False).count()
        notifications = all_notifications[:5]
        form = AppointmentForm()
        # Today's appointments
        today_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=today
        ).order_by('appointment_time').select_related('patient')
        
        # Upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=today,
            appointment_date__lte=today + timedelta(days=7)
        ).exclude(
            appointment_date=today
        ).select_related('patient').order_by('appointment_date', 'appointment_time')[:5]
        
        # Recent patients (NO slice until the end)
        recent_patients = Patient.objects.filter(
            appointments__doctor=doctor
        ).order_by('-appointments__appointment_date').distinct()[:4]
        
        # Key metrics
        total_patients = Patient.objects.filter(
            appointments__doctor=doctor
        ).distinct().count()
        
        pending_appointments = Appointment.objects.filter(
            doctor=doctor,
            status='pending'
        ).count()
        
        this_month_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__year=today.year,
            appointment_date__month=today.month
        ).count()
        
        # Context with ALL data
        context = {
            'doctor': doctor,
            'today': today,
            'today_appointments': today_appointments,
            'recent_appointments': today_appointments,
            'upcoming_appointments': upcoming_appointments,
            'recent_patients': recent_patients,
            'total_patients': total_patients,
            'pending_count': pending_appointments,
            'month_appointments': this_month_appointments,
            'avg_rating': 4.5,  # Or calculate from Review model
            'notifications': notifications,  # ✅ Already sliced
            'unread_notifications_count': unread_count,  # ✅ Counted BEFORE slice
            'form':form,
        }
        
        return render(request, 'doctor_dashboard.html', context)

@login_required
def patients_list(request):
    try:
        # Get the Doctor profile for the logged-in user
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = None
        # Handle case where doctor profile doesn't exist (return empty list)
        return render(request, 'patients_list.html', {'page_obj': None})

    # Use 'doctors' (plural) to match your model field name
    all_patients = Patient.objects.filter(doctors=doctor).order_by('-created_at')

    # Search Logic
    query = request.GET.get('q')
    if query:
        all_patients = all_patients.filter(
            first_name__icontains=query
        ) | all_patients.filter(
            last_name__icontains=query
        )

    # Pagination
    paginator = Paginator(all_patients, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'doctor': doctor
    }
    
    return render(request, 'patients_list.html', context)

@login_required
def add_medical_record(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    try:
        doctor = request.user.doctor_profile # Or Doctor.objects.get(user=request.user)
    except:
        messages.error(request, "You must be a doctor to add records.")
        return redirect('webapp:patients_list')

    if request.method == 'POST':
        # Get text data
        symptoms = request.POST.get('symptoms')
        diagnosis = request.POST.get('diagnosis')
        treatment = request.POST.get('treatment_plan')
        medicine = request.POST.get('medicine')
        follow_up = request.POST.get('follow_up_date')
        
        # CRITICAL CHANGE 3: Get the file data
        attachment_file = request.FILES.get('attachment') 

        if not follow_up:
            follow_up = None

        # Create the record
        PatientRecord.objects.create(
            patient=patient,
            doctor=doctor,
            symptoms=symptoms,
            diagnosis=diagnosis,
            treatment_plan=treatment,
            medicine=medicine,
            follow_up_date=follow_up,
            attachment=attachment_file  # <--- Save the file here
        )

        messages.success(request, f'Medical record added for {patient.first_name}.')
    
    return redirect('patients_list')

@login_required
def appointments_list(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    
    q = request.GET.get('q', '').strip()
    qs = Appointment.objects.filter(doctor=doctor).select_related('patient')
    form = AppointmentForm()
    if q:
        qs = qs.filter(
            Q(patient__first_name__icontains=q) |
            Q(patient__last_name__icontains=q) |
            Q(appointment_type__icontains=q) |
            Q(status__icontains=q)
        )
    
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'doctor': doctor,
        'page_obj': page_obj,
        'form':form,
    }
    return render(request, 'doctor_appointments.html', context)
@login_required
def appointment_create(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.save()
            patient = appointment.patient
            patient.doctors.add(doctor)
            messages.success(request, 'Appointment created successfully.')
            # Redirect back to the main appointments page
            return redirect('doctor_appontments') 
        else:
            # Optional: Add form errors to messages if invalid
            messages.error(request, 'Error creating appointment. Please check inputs.')
            
    # If GET request, just go back to the dashboard (since modal is on the dashboard)
    return redirect('doctor_appontments')


# --- 2. EDIT APPOINTMENT (Action Only) ---
@login_required
def appointment_edit(request, pk):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully.')
        else:
           for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
    # Redirect back to the main appointments page
    return redirect('doctor_appontments')


# --- 3. DELETE APPOINTMENT (Action Only) ---
@login_required
def appointment_delete(request, pk):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully.')

    # Redirect back to the main appointments page
    return redirect('doctor_appontments')


@login_required
def consultations_list(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    qs = Consultation.objects.filter(doctor=doctor).select_related('patient')
    consultation_form = ConsultationForm()

    if q:
        qs = qs.filter(
            Q(patient__first_name__icontains=q) |
            Q(patient__last_name__icontains=q) |
            Q(diagnosis__icontains=q) |
            Q(consultation_type__icontains=q)
        )

    if status:
        qs = qs.filter(status=status)

    qs = qs.order_by('-date')

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'doctor': doctor,
        'page_obj': page_obj,
        'consultation_form': consultation_form,
    }
    return render(request, 'consultations.html', context)

@login_required
def consultation_create(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.doctor = doctor
            consultation.save()
            messages.success(request, 'Consultation record added successfully.')
        else:
            messages.error(request, 'Error adding consultation. Please check inputs.')
            
    # Redirect back to the consultations list
    return redirect('consultations')

# --- EDIT CONSULTATION ---
@login_required
def consultation_edit(request, pk):
    # Security: Ensure the doctor exists and owns this consultation
    doctor = get_object_or_404(Doctor, user=request.user)
    consultation = get_object_or_404(Consultation, pk=pk, doctor=doctor)

    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consultation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consultation updated successfully.')
        else:
            # Show specific errors if update fails
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    # Redirect back to the consultation list (change name if yours is different)
    return redirect('consultations')

# --- DELETE CONSULTATION ---
@login_required
def consultation_delete(request, pk):
    # Security: Ensure ownership
    doctor = get_object_or_404(Doctor, user=request.user)
    consultation = get_object_or_404(Consultation, pk=pk, doctor=doctor)

    if request.method == 'POST':
        consultation.delete()
        messages.success(request, 'Consultation deleted successfully.')
    
    return redirect('consultations')

@login_required
def doctor_settings(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    
    # Initialize forms with current data
    profile_form = DoctorProfileForm(instance=doctor)
    # USE NEW CLASS NAME HERE
    notification_form = DoctorNotificationForm(instance=doctor)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        # --- ACTION 1: UPDATE PROFILE ---
        if 'update_profile' in request.POST:
            profile_form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('doctor-settings')

        # --- ACTION 2: CHANGE PASSWORD ---
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) 
                messages.success(request, 'Password changed successfully!')
                return redirect('doctor-settings')
            else:
                messages.error(request, 'Please correct the error in the password form.')

        # --- ACTION 3: NOTIFICATIONS ---
        elif 'update_notifications' in request.POST:
            # USE NEW CLASS NAME HERE
            notification_form = DoctorNotificationForm(request.POST, instance=doctor)
            if notification_form.is_valid():
                notification_form.save()
                messages.success(request, 'Notification preferences saved.')
                return redirect('doctor-settings')

    context = {
        'doctor': doctor,
        'profile_form': profile_form,
        'notification_form': notification_form,
        'password_form': password_form,
    }
    return render(request, 'doctor_settings.html', context)


def logout_view(request):
    logout(request)
    return redirect('landing')


@login_required
def patient_dashboard(request):
    patient = get_object_or_404(Patient, user=request.user)

    # Latest readings per type for this patient
    latest_heart = (WearableDevice.objects
                    .filter(patient=patient, reading_type='heart_rate')
                    .order_by('-time')
                    .first())
    latest_bp = (WearableDevice.objects
                 .filter(patient=patient, reading_type='blood_pressure')
                 .order_by('-time')
                 .first())
    latest_temp = (WearableDevice.objects
                   .filter(patient=patient, reading_type='temperature')
                   .order_by('-time')
                   .first())
    latest_spo2 = WearableDevice.objects.filter(
    patient=patient, reading_type='oxygen_saturation').order_by('-time').first()
    appointment_form = PatientBookAppointmentForm()

    # Device stats
    total_devices = WearableDevice.objects.filter(patient=patient).count()
    active_devices = WearableDevice.objects.filter(patient=patient, is_active=True).count()

    # Next upcoming appointment
    today = timezone.localdate()
    now_time = timezone.localtime().time()
    next_appointment = (Appointment.objects
                        .filter(patient=patient,
                                appointment_date__gte=today,
                                status__in=['pending', 'confirmed'])
                        .order_by('appointment_date', 'appointment_time')
                        .first())
    notifications = (
    Notification.objects
    .filter(patient=patient)
    .select_related('doctor')
    .order_by('-created_at')[:5]   
)
    unread_count = Notification.objects.filter(patient=patient, is_read=False).count()
    devices = WearableDevice.objects.filter(patient=patient).order_by('-time')
    appt_qs = Appointment.objects.filter(patient=patient)
    paginator = Paginator(appt_qs, 4)  # 4 cards per page
    page_number = request.GET.get("page")
    appt_page = paginator.get_page(page_number)

    context = {
        "patient": patient,
        "latest_heart": latest_heart,
        "latest_bp": latest_bp,
        "latest_temp": latest_temp,
        "total_devices": total_devices,
        "active_devices": active_devices,
        "next_appointment": next_appointment,
        "notifications": notifications,
        "unread_count": unread_count,
        "latest_spo2": latest_spo2,
        "devices": devices,
        "appt_page": appt_page,
        'appointment_form': appointment_form,
    }
    return render(request, "patientdashboard.html", context)

@login_required
def find_doctors_view(request):
    # 1. Get Filter Parameters
    q = request.GET.get("q", "").strip()
    specialty = request.GET.get("specialty", "")
    location = request.GET.get("location", "")
    sort = request.GET.get("sort", "price_asc")

    # 2. Start with all doctors
    doctors_qs = Doctor.objects.all()

    # 3. Apply Search (Name or Specialty)
    if q:
        doctors_qs = doctors_qs.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(specialization__icontains=q)
        )

    # 4. Filter by Specialty
    if specialty and specialty != "all":
        doctors_qs = doctors_qs.filter(specialization__iexact=specialty)

    # 5. Filter by District (Location)
    if location and location != "all":
        doctors_qs = doctors_qs.filter(primary_practice_district__iexact=location)

    # 6. Annotate Data (Fees, Ratings)
    # Subquery: get the consultation fee from the primary hospital relationship
    fee_subquery = DoctorHospital.objects.filter(
            doctor=OuterRef("pk")
            # We removed the filter!
        ).values('hospital__consultation_fee')[:1]

    doctors_qs = doctors_qs.annotate(
        avg_rating=Avg("reviews__rating"),
        review_count=Count("reviews"),
        consultation_fee=Subquery(fee_subquery)
    )

    # 7. Apply Sorting
    if sort == "price_desc":
        # Sort by fee high-to-low. Use 0 as fallback if fee is None
        doctors_qs = doctors_qs.order_by("-consultation_fee")
    elif sort == "price_asc":
        doctors_qs = doctors_qs.order_by("consultation_fee")
    else:
        # Default: Sort by rating high-to-low
        doctors_qs = doctors_qs.order_by("-avg_rating")

    # 8. Pagination (6 doctors per page)
    paginator = Paginator(doctors_qs, 6)
    page_number = request.GET.get("page")
    doctors_page = paginator.get_page(page_number)

    # 9. Get unique values for dropdowns (Ordered alphabetically)
    unique_locations = Doctor.objects.values_list(
        "primary_practice_district", flat=True
    ).distinct().order_by("primary_practice_district")
    
    unique_specialties = Doctor.objects.values_list(
        "specialization", flat=True
    ).distinct().order_by("specialization")
    booking_form = PatientBookAppointmentForm()

    context = {
        "doctors_page": doctors_page,
        "booking_form": booking_form,
        # Pass filter lists to the template
        "locations": unique_locations,
        "specialties": unique_specialties,
        
        # Pass current selections back (to keep dropdowns selected)
        "q": q,
        "selected_specialty": specialty,
        "selected_location": location,
        "sort": sort,
    }

    return render(request, "find_doctors.html", context)

@login_required
def triage_page(request):
    """Display the triage assessment page"""
    return render(request, 'ai_tirag.html')

@login_required
def patient_profile_settings(request):
    patient = get_object_or_404(Patient, user=request.user)
    prefs, _ = PatientNotificationPreference.objects.get_or_create(patient=patient)

    # Initialize forms with POST data if available, else standard
    profile_form = PatientProfileForm(instance=patient, user=request.user)
    password_form = PasswordChangeForm(request.user)
    record_form = PatientUploadForm() # Use the simplified upload form
    prefs_form = PatientNotificationPreferenceForm(instance=prefs)

    if request.method == "POST":
        # --- 1. PROFILE UPDATE ---
        if "profile_submit" in request.POST:
            profile_form = PatientProfileForm(request.POST, request.FILES, instance=patient, user=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("patient-settings")
            else:
                 messages.error(request, "Please correct the errors in your profile.")

        # --- 2. PASSWORD UPDATE ---
        elif "password_submit" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # Keeps user logged in
                messages.success(request, "Password updated successfully.")
                return redirect("patient-settings")
            else:
                messages.error(request, "Please correct the errors in your password.")

        # --- 3. MEDICAL RECORD UPLOAD ---
        elif "record_submit" in request.POST:
            record_form = PatientUploadForm(request.POST, request.FILES)
            if record_form.is_valid():
                rec = record_form.save(commit=False)
                rec.patient = patient
                # Optional: Mark as "Patient Uploaded" if you have a type field
                # rec.record_type = 'Patient Upload' 
                rec.save()
                messages.success(request, "Medical record uploaded.")
                return redirect("patient-settings")
            else:
                messages.error(request, "Failed to upload record. Please select a valid file.")

        # --- 4. NOTIFICATIONS UPDATE ---
        elif "notifications_submit" in request.POST:
            prefs_form = PatientNotificationPreferenceForm(request.POST, instance=prefs)
            if prefs_form.is_valid():
                prefs_form.save()
                messages.success(request, "Notification preferences updated.")
                return redirect("patient-settings")

    # Fetch records for display
    records = patient.medical_records.all().order_by('-created_time')


    context = {
        "patient": patient,
        "profile_form": profile_form,
        "password_form": password_form,
        "record_form": record_form,
        "prefs_form": prefs_form,
        "records": records,
    }
    return render(request, "patient_settings.html", context)

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = PatientBookAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            try:
                # 1. Get the Patient profile
                patient_profile = Patient.objects.get(user=request.user)
                appointment.patient = patient_profile
                appointment.status = 'pending'
                
                # 2. Save the Appointment first
                appointment.save()

                # 3. LINK THEM TIGHTLY (Your suggestion)
                # This adds the doctor to the patient's "My Doctors" list
                patient_profile.doctors.add(appointment.doctor)

                messages.success(request, "Appointment booked and Doctor added to your list!")
                return redirect('patient_dashboard')

            except Patient.DoesNotExist:
                messages.error(request, "Error: Patient profile not found.")
                return redirect('patient_dashboard')
                
    return redirect('patient_dashboard')

@login_required
def cancel_appointment(request, appointment_id):
    if request.method == "POST":
        # Get the appointment, ensuring it belongs to the logged-in patient
        appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)
        
        if appointment.status != 'cancelled':
            appointment.status = 'cancelled'
            appointment.save()
            messages.success(request, "Appointment cancelled successfully.")
        else:
            messages.warning(request, "This appointment is already cancelled.")
            
    return redirect('patient_dashboard')
# Alternative: Function-based view (simpler, but class-based recommended for larger projects)
"""@login_required(login_url='login')
def doctor_dashboard(request):
    #Function-based view for doctor dashboard
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return render(request, 'error.html', {
            'error': 'Doctor profile not found'
        })
    
    today = timezone.now().date()
    
    # Fetch data (same logic as above)
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).order_by('appointment_time').select_related('patient')
    
    # ... rest of metrics calculation
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        # ... other context variables
    }
    
    return render(request, 'doctors/dashboard.html', context)"""