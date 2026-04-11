from django.contrib import admin

from .models import User,Car,Purchase,Notification,TestDrive,Cart,CarComparison,Invoice,EMIHistory

# Register your models here.

admin.site.register(User)
admin.site.register(Car)
admin.site.register(Purchase)
admin.site.register(Notification)
admin.site.register(TestDrive)
admin.site.register(Cart)   
admin.site.register(CarComparison)
admin.site.register(Invoice)    
admin.site.register(EMIHistory)
