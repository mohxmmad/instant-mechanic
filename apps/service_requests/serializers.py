from rest_framework import serializers
from .models import ServiceRequest
from .validators import validate_phone, validate_vehicle_number

ALLOWED_STATUSES = {c[0] for c in ServiceRequest.Status.choices}
# Valid transitions
VALID_TRANSITIONS = {
    ServiceRequest.Status.PENDING: {ServiceRequest.Status.IN_PROGRESS, ServiceRequest.Status.CANCELLED},
    ServiceRequest.Status.IN_PROGRESS: {ServiceRequest.Status.COMPLETED, ServiceRequest.Status.CANCELLED},
    ServiceRequest.Status.COMPLETED: set(),
    ServiceRequest.Status.CANCELLED: set(),
}

class ServiceRequestSerializer(serializers.ModelSerializer):
    customer_phone = serializers.CharField()
    vehicle_number = serializers.CharField()
    # mechanic is writable PK

    class Meta:
        model = ServiceRequest
        fields = [
            "id", "customer_name", "customer_phone", "vehicle_number",
            "mechanic", "service", "problem_description", "status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_customer_phone(self, value):
        return validate_phone(value)

    def validate_vehicle_number(self, value):
        return validate_vehicle_number(value)

    def validate_customer_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Customer name cannot be blank.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Customer name must be at least 2 characters.")
        return value.strip()

    def validate_service(self, value):
        if not value.strip():
            raise serializers.ValidationError("Service cannot be blank.")
        return value.strip()

    def validate_status(self, value):
        if value not in ALLOWED_STATUSES:
            raise serializers.ValidationError(f"Invalid status. Allowed: {', '.join(ALLOWED_STATUSES)}")
        return value

    def validate(self, attrs):
        # Status transition validation on update
        if self.instance is not None and "status" in attrs:
            old_status = self.instance.status
            new_status = attrs["status"]
            if old_status != new_status:
                allowed = VALID_TRANSITIONS.get(old_status, set())
                if new_status not in allowed:
                    raise serializers.ValidationError(
                        {"status": f"Invalid status transition from {old_status} to {new_status}. Allowed: {sorted(allowed) if allowed else 'no transitions'}"}
                    )
        return attrs

    def validate_mechanic(self, value):
        # value is Mechanic instance due to PrimaryKeyRelatedField
        if value is None:
            raise serializers.ValidationError("Mechanic does not exist.")
        return value
