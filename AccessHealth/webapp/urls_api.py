from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_api

# Create a router and register our viewsets with it.
router = DefaultRouter()

# Registering endpoints
router.register(r'hospitals', views_api.HospitalViewSet)
router.register(r'doctor-hospitals', views_api.DoctorHospitalViewSet)
router.register(r'patients', views_api.PatientViewSet)
router.register(r'doctors', views_api.DoctorViewSet)
router.register(r'reviews', views_api.ReviewViewSet)
router.register(r'wearables', views_api.WearableDeviceViewSet)
router.register(r'patient-records', views_api.PatientRecordViewSet)
router.register(r'appointments', views_api.AppointmentViewSet)
router.register(r'consultations', views_api.ConsultationViewSet)
router.register(r'notifications', views_api.NotificationViewSet)
router.register(r'patient-preferences', views_api.PatientNotificationPreferenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]