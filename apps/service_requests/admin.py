from django.contrib import admin
from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "customer_phone", "vehicle_number", "mechanic", "service", "status", "created_at")
    list_filter = ("status", "service", "created_at")
    search_fields = ("customer_name", "vehicle_number", "customer_phone")
    list_select_related = ("mechanic",)
