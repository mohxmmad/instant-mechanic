import re
from rest_framework import serializers

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

VEHICLE_REGEX = re.compile(r"^[A-Z]{2}\s?\d{1,2}\s?[A-Z]{1,3}\s?\d{1,4}$", re.IGNORECASE)

def validate_vehicle_number(value: str):
    # Accept Indian format like MH01AB1234, DL 8C AB 1234 etc, also simpler alphanumeric with spaces/dashes
    normalized = value.strip().upper().replace("-", " ")
    # Remove extra spaces
    normalized = re.sub(r"\s+", " ", normalized)
    # Basic check: must be alphanumeric, 5-15 chars ignoring spaces
    alnum = re.sub(r"\s+", "", normalized)
    if not re.fullmatch(r"[A-Z0-9]{5,15}", alnum):
        raise serializers.ValidationError("Invalid vehicle number. Must be 5-15 alphanumeric characters (e.g., MH01AB1234).")
    # Optionally enforce Indian pattern but allow flexible
    # If it looks like Indian format, validate stricter; otherwise accept generic
    return normalized
