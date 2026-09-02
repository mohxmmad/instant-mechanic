from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MechanicViewSet

router = DefaultRouter()
router.register(r"mechanics", MechanicViewSet, basename="mechanic")

urlpatterns = [
    path("", include(router.urls)),
]
