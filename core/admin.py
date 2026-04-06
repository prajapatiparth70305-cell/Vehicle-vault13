from django.contrib import admin

from .models import Car,Purchase,Notification

# Register your models here.

admin.site.register(Car)
admin.site.register(Purchase)
admin.site.register(Notification)

