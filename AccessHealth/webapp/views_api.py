from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Hospital, DoctorHospital, Patient, Doctor, Review, 
    WearableDevice, PatientRecord, Appointment, Notification, 
    Consultation, PatientNotificationPreference
)
from .serializers import (
    HospitalSerializer, DoctorHospitalSerializer, PatientSerializer, 
    DoctorSerializer, ReviewSerializer, WearableDeviceSerializer, 
    PatientRecordSerializer, AppointmentSerializer, NotificationSerializer, 
    ConsultationSerializer, PatientNotificationPreferenceSerializer
)

# --- Hospital Views ---
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'district']

class DoctorHospitalViewSet(viewsets.ModelViewSet):
    queryset = DoctorHospital.objects.all()
    serializer_class = DoctorHospitalSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- Patient Views ---
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser) # Supports image upload
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'patient_national_id']

class PatientNotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = PatientNotificationPreference.objects.all()
    serializer_class = PatientNotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- Doctor Views ---
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['specialization', 'district', 'gender']
    search_fields = ['first_name', 'last_name', 'specialization']

# --- Interaction Views ---
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

class WearableDeviceViewSet(viewsets.ModelViewSet):
    queryset = WearableDevice.objects.all()
    serializer_class = WearableDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

class PatientRecordViewSet(viewsets.ModelViewSet):
    queryset = PatientRecord.objects.all()
    serializer_class = PatientRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser) # Supports file upload

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'appointment_date', 'doctor', 'patient']

class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]