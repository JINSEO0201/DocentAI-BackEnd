from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    full_name = models.CharField(max_length=128, blank=True)
    access = models.CharField(max_length=1024, blank=True, unique=True)
    refresh = models.CharField(max_length=1024, blank=True, unique=True)

    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email
    
