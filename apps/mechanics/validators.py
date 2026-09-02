import re
from rest_framework import serializers

PHONE_REGEX = re.compile(r"^\+?91?[6-9]\d{9}$|^\+?\d{7,15}$")

def validate_phone(value: str):
    normalized = re.sub(r"[\s\-]", "", value)
    if not re.fullmatch(r"\+?\d{7,15}", normalized):
        raise serializers.ValidationError("Invalid phone number. Must be 7-15 digits, optionally starting with +.")
    digits = normalized.lstrip("+")
    if len(digits) == 10 and digits[0] not in "6789":
        raise serializers.ValidationError("Invalid Indian phone number. Must start with 6-9.")
    if len(digits) < 7 or len(digits) > 15:
        raise serializers.ValidationError("Phone number must be between 7 and 15 digits.")
    return normalized

ALLOWED_SERVICES = {
    "engine repair",
    "oil change",
    "brake service",
    "tire replacement",
    "battery replacement",
    "ac repair",
    "denting painting",
    "general service",
    "electrical",
    "towing",
    "car wash",
    "diagnostics",
}

def validate_services(value):
    if not isinstance(value, list):
        raise serializers.ValidationError("Services must be a list.")
    if not value:
        raise serializers.ValidationError("At least one service must be provided.")
    normalized = []
    for s in value:
        if not isinstance(s, str) or not s.strip():
            raise serializers.ValidationError("Each service must be a non-empty string.")
        svc = s.strip().lower()
        normalized.append(s.strip())
    if len(set(n.lower() for n in normalized)) != len(normalized):
        raise serializers.ValidationError("Duplicate services not allowed.")
    return normalized
