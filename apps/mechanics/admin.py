from django.contrib import admin
from .models import Mechanic


@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "location", "rating", "is_open", "created_at")
    list_filter = ("location", "is_open", "rating")
    search_fields = ("name", "phone", "location")
    ordering = ("-rating",)
