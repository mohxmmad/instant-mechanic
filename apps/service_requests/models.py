from django.db import models

class ServiceRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=20, db_index=True)
    mechanic = models.ForeignKey("mechanics.Mechanic", on_delete=models.CASCADE, related_name="service_requests")
    service = models.CharField(max_length=100)
    problem_description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["mechanic", "status"]),
        ]

    def __str__(self):
        return f"SR#{self.id} - {self.customer_name} -> {self.mechanic_id} [{self.status}]"
