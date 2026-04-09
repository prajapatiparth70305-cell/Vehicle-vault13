from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
         raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(email, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser):

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
        
    email = models.EmailField(unique=True)
    

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    firstname=models.CharField(max_length=20,null=True)
    lastname=models.CharField(max_length=20,null=True)
    gender=models.CharField(max_length=10,null=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    otp_created_at = models.DateTimeField(null=True,blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    objects = UserManager()

    #override userName filed
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email


    
    
class Car(models.Model):


    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('cng', 'CNG'),
        ('electric', 'Electric'),
    ]

    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]

    MODEL_CHOICES = [
        ('EX', 'EX'),
        ('SX ', 'SX'),
        ('SX(O)', 'SX(O)'),
        ('S', 'S'),
    ]
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    model= models.CharField(max_length=100,null=True,choices=MODEL_CHOICES)
    fuel_type = models.CharField(max_length=20,null=True,choices=FUEL_CHOICES)
    price = models.IntegerField()
    mileage = models.FloatField(null=True)
    seats = models.IntegerField(null=True, blank=True)
    features = models.TextField(null=True, blank=True)
    year =models.IntegerField(null=True)
    transmission = models.CharField(max_length=20,null=True,choices=TRANSMISSION_CHOICES)
    description = models.TextField(null=True)
    image = models.ImageField(upload_to='cars/')
    def __str__(self):
        return self.name


class TestDrive(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True,blank=True)
    pickup_location = models.CharField(max_length=255,null=True,blank=True)
    date = models.DateField()
    time = models.TimeField()

    def _str_(self):
        return f"{self.user.username} - {self.car.name}"




class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user} - {self.car}"
    
class CarComparison(models.Model):
    car1 = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="car1")
    car2 = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="car2")
    compared_at = models.DateTimeField(auto_now_add=True)

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    car = models.ForeignKey('Car', on_delete=models.CASCADE,null=True)
    amount = models.IntegerField(null=True,blank=True)
    payment_id = models.CharField(max_length=200,null=True)
    status = models.CharField(max_length=50,null=True)
    date = models.DateTimeField(auto_now_add=True,null=True)

    is_insurance = models.BooleanField(default=False,null=True)
    insurance_plan = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_expired = models.BooleanField(default=False,null=True)
    def _str_(self):
        return self.car_name


    

class Invoice(models.Model):


    car = models.ForeignKey('Car', on_delete=models.CASCADE)
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE)

    invoice_number = models.CharField(max_length=100)
    amount = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number
    
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('success', 'Success'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} - {self.message[:20]}"
 

class EMIHistory(models.Model):
    payment_id = models.CharField(max_length=200)
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    car_name=models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    next_due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False,null=True)
    total_emi = models.IntegerField(null=True, blank=True)
    paid_emi = models.IntegerField(null=True, blank=True)

    def get_status(self):
        today = timezone.now().date()

        if self.next_due_date:
            if today > self.next_due_date:
                return "Overdue ❌"
            elif self.next_due_date - today <= timedelta(days=3):
                return "Due Soon ⚠️"
            else:
                return "Paid ✅"

        return "Not Set"
    
    def remaining_emi(self):
        return(self.total_emi or 0) - (self.paid_emi or 0)

    def _str_(self):
        return self.payment_id 