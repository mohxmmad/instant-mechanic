import logging
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


@extend_schema(
    description="Health check endpoint - verifies database connectivity.",
    responses={200: dict},
    auth=[],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        db_status = "connected"
        status = "healthy"
    except Exception as exc:
        logger.error("Health check database failure: %s", exc, exc_info=True)
        db_status = "disconnected"
        status = "unhealthy"
        return Response({"status": status, "database": db_status}, status=500)

    return Response({"status": status, "database": db_status})
