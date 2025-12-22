from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Hospital, DoctorHospital, Patient, Doctor, Review, 
    WearableDevice, PatientRecord, Appointment, Notification, 
    Consultation, PatientNotificationPreference
)

User = get_user_model()

# --- Helper Serializer for User Info ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        ref_name = "AppUser"  # Avoid conflict with other User serializers

# --- Hospital Serializers ---
class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'

class DoctorHospitalSerializer(serializers.ModelSerializer):
    hospital_name = serializers.ReadOnlyField(source='hospital.name')
    doctor_name = serializers.ReadOnlyField(source='doctor.full_name')

    class Meta:
        model = DoctorHospital
        fields = '__all__'

# --- Patient Serializers ---
class PatientNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientNotificationPreference
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    age = serializers.ReadOnlyField()
    notification_prefs = PatientNotificationPreferenceSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['user']

# --- Doctor Serializers ---
class DoctorSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    full_name = serializers.ReadOnlyField()
    avg_rating = serializers.FloatField(source='get_avg_rating', read_only=True)
    
    class Meta:
        model = Doctor
        fields = '__all__'
        read_only_fields = ['user']

# --- Review Serializer ---
class ReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.ReadOnlyField(source='patient.user.get_full_name')

    class Meta:
        model = Review
        fields = '__all__'

# --- Device & Records Serializers ---
class WearableDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WearableDevice
        fields = '__all__'

class PatientRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientRecord
        fields = '__all__'

# --- Appointment & Consultation Serializers ---
class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.full_name')
    patient_name = serializers.ReadOnlyField(source='patient.user.get_full_name')
    datetime = serializers.ReadOnlyField()

    class Meta:
        model = Appointment
        fields = '__all__'

class ConsultationSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.full_name')
    patient_name = serializers.ReadOnlyField(source='patient.user.get_full_name')

    class Meta:
        model = Consultation
        fields = '__all__'

# --- Notification Serializer ---
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'