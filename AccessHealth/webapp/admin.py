from django.contrib import admin
from .models import *
admin.site.register(Patient)
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'years_of_experience', 'phone_number')
    list_filter = ('specialization', 'is_available')
    search_fields = ('first_name', 'last_name', 'doctor_licence_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
admin.site.register(PatientRecord)
admin.site.register(WearableDevice)
admin.site.register(Notification)
admin.site.register(Hospital)
admin.site.register(Appointment)
admin.site.register(DoctorHospital)
admin.site.register(Consultation)
admin.site.register(PatientNotificationPreference)
# Register your models here.
