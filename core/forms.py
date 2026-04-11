from django.contrib.auth.forms import UserCreationForm
from .models import User,Car
from django import forms

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]

class UserSignupForm(UserCreationForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    class Meta:

        model=User
        fields=['email', 'password1', 'password2', 'firstname', 'lastname', 'gender', 'mobile', 'date_of_birth', 'address']
        widgets={
            'password1':forms.PasswordInput(),
            'password2':forms.PasswordInput(),
            
        }

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields ='__all__'






