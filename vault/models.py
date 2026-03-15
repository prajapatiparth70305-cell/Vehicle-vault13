from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Vehicle(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20)
    brand = models.CharField(max_length=50)
    entry_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vehicle_number
    
