from rest_framework import serializers
from .models import Mechanic
from .validators import validate_phone, validate_services

class MechanicSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(validators=[])
    services = serializers.ListField(child=serializers.CharField(), allow_empty=False)

    class Meta:
        model = Mechanic
        fields = ["id", "name", "phone", "location", "rating", "is_open", "services", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_phone(self, value):
        return validate_phone(value)

    def validate_services(self, value):
        return validate_services(value)

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be blank.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        return value.strip()

    def validate_location(self, value):
        if not value.strip():
            raise serializers.ValidationError("Location cannot be blank.")
        return value.strip()
