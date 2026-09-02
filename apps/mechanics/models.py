from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Mechanic(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    phone = models.CharField(max_length=15, db_index=True)
    location = models.CharField(max_length=100, db_index=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("5"))])
    is_open = models.BooleanField(default=True, db_index=True)
    services = models.JSONField(default=list, help_text="List of services offered")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["location", "is_open"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.location})"
