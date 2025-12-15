from django import forms
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import datetime

class DoctorSignupForm(forms.ModelForm):
    hospital = forms.ModelChoiceField(
        queryset=Hospital.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Doctor
        fields = [
            'doctor_licence_number',
            'first_name',
            'last_name',
            'dob',
            'district',
            'sector',
            'gender',
            'phone_number',
            'specialization',
            'years_of_experience',
            'professional_bio',
            
        ]
        widgets = {
            'professional_bio': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        cpwd = cleaned_data.get('confirm_password')
        if pwd and cpwd and pwd != cpwd:
            self.add_error('confirm_password', "Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        cleaned = self.cleaned_data
        email = cleaned['email']
        password = cleaned['password']
        selected_hospital = cleaned['hospital']

        # 1) create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # 2) create doctor profile
        doctor = super().save(commit=False)
        doctor.user = user
        # Optional: also fill the text field with hospital name
        doctor.hospital_or_clinic_affiliation = selected_hospital.name

        if commit:
            doctor.save()

            # 3) link doctor to hospital via DoctorHospital
            DoctorHospital.objects.create(
                doctor=doctor,
                hospital=selected_hospital,
                is_primary_location=True
            )

        return doctor

class PatientSignupForm(forms.ModelForm):
    # User-related fields
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Patient
        fields = [
            'patient_national_id',
            'first_name',
            'last_name',
            'dob',
            'gender',
            'district',
            'sector',
            'phone_number',
            'blood_type',       
            'emergency_contact',
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        cpwd = cleaned_data.get('confirm_password')
        if pwd and cpwd and pwd != cpwd:
            self.add_error('confirm_password', "Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        cleaned = self.cleaned_data
        email = cleaned['email']
        password = cleaned['password']

        user = User.objects.create_user(
            username=cleaned['email'],
            email=email,
            password=password,
            first_name=cleaned['first_name'],
            last_name=cleaned['last_name'],
        )

        patient = super().save(commit=False)
        patient.user = user
        if commit:
            patient.save()
        return patient



class PatientLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))

class DoctorLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        print("DEBUG User type:", type(User))
        if not email or not password:
            return cleaned_data

        # User here is the imported model
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.add_error('email', 'No account found with this email')
            return cleaned_data

        authenticated_user = authenticate(
            username=user.username,
            password=password
        )
        if authenticated_user is None:
            self.add_error('password', 'Incorrect password')

        # store for later use
        self._user = authenticated_user
        return cleaned_data

    def get_user(self):
        return getattr(self, '_user', None)




class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        # 1. Added 'status' to the fields list
        fields = ['patient', 'appointment_date', 'appointment_time', 'appointment_type', 'status', 'notes']
        
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select border-start-0'}),
            'appointment_type': forms.Select(attrs={'class': 'form-select border-start-0'}),
            'status': forms.Select(attrs={'class': 'form-select border-start-0'}),
            
            # 2. Changed Date and Time to standard HTML5 inputs
            'appointment_date': forms.DateInput(attrs={'class': 'form-control border-start-0', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control border-start-0', 'type': 'time'}),
            
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('appointment_date')
        time = cleaned_data.get('appointment_time')

        if date and time:
            # 1. Check if the date is in the past
            if date < datetime.date.today():
                raise ValidationError("You cannot book appointments in the past.")

            # 2. Check Database for conflicts
            conflicting_appointment = Appointment.objects.filter(
                appointment_date=date,
                appointment_time=time
            )

            # If editing, exclude the current appointment from the check
            if self.instance.pk:
                conflicting_appointment = conflicting_appointment.exclude(pk=self.instance.pk)

            if conflicting_appointment.exists():
                raise ValidationError("This time slot is already booked. Please choose a different time.")

        return cleaned_data


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = [
            'patient', 'appointment', 'date', 'start_time', 'end_time',
            'consultation_type', 'duration_minutes', 'chief_complaint',
            'history', 'examination', 'diagnosis', 'treatment_plan',
            'medications', 'follow_up_instructions', 'status', 'notes'
        ]
        widgets = {
            # Dropdowns
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'consultation_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),

            # Date & Time
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '5', 'step': '5'}),

            # Text Fields (Single Line)
            'chief_complaint': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Main symptom...'}),
            'diagnosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Final diagnosis...'}),

            # Text Areas (Multi Line)
            'history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Patient history...'}),
            'examination': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Physical exam findings...'}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Plan details...'}),
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Prescribed meds...'}),
            'follow_up_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name', 'phone_number', 'specialization', 
                  'district', 'sector', 'hospital_or_clinic_affiliation', 'profile_image', 'professional_bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'sector': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_or_clinic_affiliation': forms.TextInput(attrs={'class': 'form-control'}),
            'professional_bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

# 2. Notification Preferences Form (RENAMED)
class DoctorNotificationForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['notify_email', 'notify_sms', 'notify_in_app']
        widgets = {
            'notify_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_in_app': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        
class PatientRecordForm(forms.ModelForm):
    class Meta:
        model = PatientRecord
        fields = ['doctor', 'attachment', 'follow_up_date',
                  'medicine', 'treatment_plan', 'symptoms', 'diagnosis']
        
class PatientUploadForm(forms.ModelForm):
    """
    A simplified form for patients to upload documents.
    They don't fill in diagnosis/medicine/doctor fields.
    """
    class Meta:
        model = PatientRecord
        fields = ['attachment'] # Only ask for the file
        widgets = {
            'attachment': forms.FileInput(attrs={'class': 'form-control', 'required': True})
        }

# --- 2. UPDATED PROFILE FORM ---
class PatientProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'dob', 'gender',
            'district', 'sector', 'phone_number',
            'blood_type', 'address', 'emergency_contact', 'avatar',
        ]
        
        BLOOD_CHOICES = [
            ('', 'Select Blood Type'),
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ]

        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'avatar': forms.FileInput(attrs={'style': 'display: none;', 'id': 'avatar-upload'}),
            'blood_type': forms.Select(choices=BLOOD_CHOICES, attrs={'class': 'form-select'}),
            
            # --- THE FIX IS HERE ---
            # 1. Remove 'gender' from widgets (Let the Model handle the dropdown automatically)
            
            # 2. Change District & Sector to TextInput (so "Gicumbi" shows up)
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter District'}),
            'sector': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Sector'}),
            
            # Ensure address is a text input too
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        
        # --- THE FIX: Pre-fill User Fields ---
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name

        # Add CSS class to all fields
        for name, field in self.fields.items():
            if name != 'avatar': 
                # Preserve existing classes if any (like form-select)
                existing_classes = field.widget.attrs.get('class', '')
                if 'form-control' not in existing_classes and 'form-select' not in existing_classes:
                     field.widget.attrs['class'] = f"{existing_classes} form-control".strip()

    def save(self, commit=True):
        patient = super().save(commit=False)
        if self.user:
            # Save the changes back to the User table
            self.user.email = self.cleaned_data['email']
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            
            if commit:
                self.user.save()
                patient.user = self.user
                patient.save()
        return patient

# --- 3. NOTIFICATION FORM ---
class PatientNotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = PatientNotificationPreference
        fields = [
            'email_appointment', 'email_health_alerts',
            'sms_appointment', 'sms_health_alerts',
        ]
        widgets = {
            'email_appointment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_health_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_appointment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_health_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PatientBookAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'appointment_type', 'notes']
        
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'appointment_type': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your symptoms...'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(PatientBookAppointmentForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].empty_label = "Select a Doctor"

    def clean(self):
        """
        Custom validation to prevent double-booking the same doctor
        at the same date and time.
        """
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appt_date = cleaned_data.get('appointment_date')
        appt_time = cleaned_data.get('appointment_time')

        if doctor and appt_date and appt_time:
            # Check if an appointment already exists
            # We use .exclude(status='cancelled') because if a slot was cancelled, 
            # it should be available again.
            exists = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appt_date,
                appointment_time=appt_time
            ).exclude(status='cancelled').exists()

            if exists:
                # This raises an error that displays at the top of the form
                raise forms.ValidationError(
                    "This doctor is already booked for this specific date and time. Please choose a different time slot."
                )
        
        return cleaned_data