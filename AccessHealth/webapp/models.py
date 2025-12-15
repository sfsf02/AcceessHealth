from django.db import models
from django.conf import settings
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name
    
class DoctorHospital(models.Model):
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE, related_name="doctor_hospitals")
    hospital = models.ForeignKey("Hospital", on_delete=models.CASCADE, related_name="hospital_doctors")

    # optional extra data
    is_primary_location = models.BooleanField(default=False)
    available_days = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("doctor", "hospital")

    def __str__(self):
        return f"{self.doctor} @ {self.hospital} ({self.consultation_fee} RWF)"

CustomUser = settings.AUTH_USER_MODEL 
# Profile for Patients
class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    patient_national_id = models.CharField(max_length=16, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    district = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    blood_type = models.CharField(max_length=3, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/patients/', blank=True, null=True)
    doctors = models.ManyToManyField('Doctor', related_name='patients')
    HEALTH_STATUS_CHOICES = [
        ('stable', 'Stable'),
        ('monitoring', 'Monitoring'),
        ('improved', 'Improved'),
        ('critical', 'Critical'),
        ('scheduled', 'Scheduled'),
    ]
    health_status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        default='scheduled'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    property
    def age(self):
        today = date.today()
        if self.dob:
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None
    @property
    def last_visit(self):
        # 1. Get appointments linked to this patient
        # 2. Filter only 'completed' appointments (so future bookings don't count)
        # 3. Order by newest date first
        # 4. Take the first one
        last_appt = self.appointments.filter(status='completed').order_by('-appointment_date').first()
        
        if last_appt:
            return last_appt.appointment_date
        return None


# Profile for Doctors
class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('CARDIOLOGY', 'Cardiology'),
        ('NEUROLOGY', 'Neurology'),
        ('ORTHOPEDICS', 'Orthopedics'),
        ('PEDIATRICS', 'Pediatrics'),
        ('PSYCHIATRY', 'Psychiatry'),
        ('ONCOLOGY', 'Oncology'),
        ('GENERAL', 'General Practice'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    doctor_licence_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Medical license number"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    district = models.CharField(max_length=100,default="kigali")
    sector = models.CharField(max_length=100,default="Gasabo")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    primary_practice_district = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    hospital_or_clinic_affiliation = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    specialization = models.CharField(
        max_length=100,
        choices=SPECIALIZATION_CHOICES
    )
    years_of_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    professional_bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='doctor_profiles/',
        blank=True,
        null=True
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notify_email = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=False)
    notify_in_app = models.BooleanField(default=True)
    hospitals = models.ManyToManyField(
        Hospital,
        through="DoctorHospital",
        related_name="doctors",
        blank=True,
    )
    
    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['specialization']),
            models.Index(fields=['hospital_or_clinic_affiliation']),
        ]
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"Dr. {self.first_name} {self.last_name}"
    
    def get_avg_rating(self):
        """Get average rating from reviews"""
        from django.db.models import Avg
        return self.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    
    def get_total_patients(self):
        """Get count of unique patients"""
        return self.appointments.values('patient').distinct().count()
    
    def get_today_appointments_count(self):
        """Get today's appointments count"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.appointments.filter(appointment_date=today).count()
    

class Review(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='doctor_reviews',
        blank=True,
        null=True
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('doctor', 'patient')  # One review per patient per doctor
    
    def __str__(self):
        return f"{self.doctor.full_name} - {self.rating}⭐"

class WearableDevice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wearable_devices')
    device_id = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=30)
    model = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    reading_type = models.CharField(max_length=50)
    value_of_reading = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20)
    time = models.DateTimeField(auto_now_add=True)
    alert = models.BooleanField(default=False)
    # allow doctors to access
    authorized_doctors = models.ManyToManyField(Doctor, blank=True, related_name='authorized_devices')

def patient_record_path(instance, filename):
    # stored under MEDIA_ROOT/patient_records/<user_id>/<filename>
    return f"patient_records/{instance.patient.user_id}/{filename}"

class PatientRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='patient_records')
    record_id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to=patient_record_path, blank=True, null=True)
    follow_up_date = models.DateField(null=True, blank=True)
    medicine = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow-up', 'Follow-up'),
        ('check-up', 'Check-up'),
        ('emergency', 'Emergency'),
    ]
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPE_CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['doctor', 'appointment_date']),
            models.Index(fields=['patient']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.doctor.full_name} - {self.patient} ({self.appointment_date})"
    
    @property
    def datetime(self):
        """Return combined datetime"""
        from datetime import datetime
        return datetime.combine(self.appointment_date, self.appointment_time)
    


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('appointment', 'Appointment'),
        ('patient', 'Patient'),
        ('message', 'Message'),
        ('reminder', 'Reminder'),
        ('system', 'System'),
    )
    
    # ✅ CHANGE THIS LINE:
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='notifications')
    # Instead of: models.ForeignKey(Customuser, ...)
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Link to related objects
    appointment = models.ForeignKey('Appointment', on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.title} - {self.doctor.user.username}"
    

# models.py
from django.db import models

class Consultation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    CONSULTATION_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow-up', 'Follow-up'),
        ('check-up', 'Check-up'),
        ('emergency', 'Emergency'),
        ('telemedicine', 'Telemedicine'),
    ]

    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    # Optional link to the source appointment
    appointment = models.ForeignKey(
        'Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultations'
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)

    consultation_type = models.CharField(
        max_length=20,
        choices=CONSULTATION_TYPE_CHOICES,
        default='consultation'
    )

    duration_minutes = models.PositiveIntegerField(default=30)

    # Clinical content
    chief_complaint = models.CharField(max_length=255, blank=True)
    history = models.TextField(blank=True)
    examination = models.TextField(blank=True)
    diagnosis = models.CharField(max_length=255, blank=True)
    treatment_plan = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['doctor', 'date']),
            models.Index(fields=['patient']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.patient} - {self.date} ({self.get_consultation_type_display()})"

    @property
    def status_badge_class(self):
        """Helper for templates to map status to CSS class."""
        return {
            'completed': 'status-completed',
            'pending': 'status-pending',
            'cancelled': 'status-cancelled',
        }.get(self.status, 'status-pending')
        

class PatientNotificationPreference(models.Model):
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='notification_prefs'
    )
    email_appointment = models.BooleanField(default=True)
    email_health_alerts = models.BooleanField(default=True)
    sms_appointment = models.BooleanField(default=False)
    sms_health_alerts = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification prefs for {self.patient.user.username}"
        

# Create your models here.
