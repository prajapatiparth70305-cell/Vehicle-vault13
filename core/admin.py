from django.contrib import admin

from .models import Car,Purchase,Invoice

# Register your models here.

admin.site.register(Car)
admin.site.register(Purchase)
admin.site.register(Invoice)
