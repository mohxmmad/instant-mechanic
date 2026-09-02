import logging
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import ServiceRequest
from .serializers import ServiceRequestSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(description="List service requests."),
    create=extend_schema(description="Create a service request for a mechanic."),
    retrieve=extend_schema(description="Retrieve service request by ID."),
    partial_update=extend_schema(description="Update status (PATCH). Valid transitions enforced."),
    update=extend_schema(description="Full update."),
    destroy=extend_schema(description="Delete service request."),
)
class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.select_related("mechanic").all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "mechanic", "service"]
    search_fields = ["customer_name", "vehicle_number", "service"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "patch", "put", "delete", "head", "options"]

    def perform_create(self, serializer):
        obj = serializer.save()
        logger.info("Service request created: id=%s mechanic=%s customer=%s", obj.id, obj.mechanic_id, obj.customer_name)

    def perform_update(self, serializer):
        obj = serializer.save()
        logger.info("Service request updated: id=%s status=%s", obj.id, obj.status)
