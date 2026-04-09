from django.contrib import admin

from .models import Car,Purchase,Notification,TestDrive

# Register your models here.

admin.site.register(Car)
admin.site.register(Purchase)
admin.site.register(Notification)
admin.site.register(TestDrive)

