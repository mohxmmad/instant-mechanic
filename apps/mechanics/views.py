import logging
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import Mechanic
from .serializers import MechanicSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(description="List mechanics with pagination, search, filtering, ordering."),
    create=extend_schema(description="Create a new mechanic."),
    retrieve=extend_schema(description="Retrieve mechanic by ID."),
    update=extend_schema(description="Full update of mechanic."),
    partial_update=extend_schema(description="Partial update of mechanic."),
    destroy=extend_schema(description="Delete mechanic."),
)
class MechanicViewSet(viewsets.ModelViewSet):
    queryset = Mechanic.objects.all()
    serializer_class = MechanicSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["location", "is_open"]
    search_fields = ["name", "location", "services"]
    ordering_fields = ["rating", "name", "created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        mechanic = serializer.save()
        logger.info("Mechanic created: id=%s name=%s", mechanic.id, mechanic.name)

    def perform_update(self, serializer):
        mechanic = serializer.save()
        logger.info("Mechanic updated: id=%s", mechanic.id)

    def perform_destroy(self, instance):
        logger.info("Mechanic deleted: id=%s name=%s", instance.id, instance.name)
        instance.delete()
