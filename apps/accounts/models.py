from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)

    # Use email as USERNAME_FIELD? Keep username for simplicity but make email unique.
    # We'll allow login with username or email via custom serializer.

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username
