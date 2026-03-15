from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import UserSignupForm,UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Car
from .forms import CarForm, TestDrive
def home(request):
    return render(request,'home.html')

def signup(request):
    if request.method =="POST":
      form = UserSignupForm(request.POST or None)
      if form.is_valid():
        # save the new user first
        user = form.save()
        email = form.cleaned_data['email']
        # prepare HTML email using the design template
        user_name = ' '.join(filter(None, [form.cleaned_data.get('first_name'), form.cleaned_data.get('last_name')])).strip() or 'User'
        context = {
            'user_name': user_name,
            'greeting': 'Welcome to Vehicle Vault!',
            'message': 'Thank you for registering with Vehicle Id. Your account has been created successfully.',
            'cta_url': request.build_absolute_uri('/'),
        }
        html_message = render_to_string('core/email_design.html', context)
        send_mail(subject='Welcome to Vehicle Vault', message=strip_tags(html_message), from_email=settings.EMAIL_HOST_USER, recipient_list=[email], html_message=html_message)
        return redirect('login')
      else:
        return render(request,'core/signup.html',{'form':form})  
    else:
        form = UserSignupForm()
        return render(request,'core/signup.html',{'form':form})
   
from django.contrib.auth import authenticate, login

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
    

    return render(request,"core/login.html")

def dashboard(request):
    return render(request,'dashboard.html')
  

def user_logout(request):
    logout(request)
    messages.success(request,"You have successfully logged out.")
    return redirect('home')

def cars(request):
    cars = Car.objects.all()
    return render(request,'cars.html',{'cars':cars})


def car_detail(request,id):
    car = get_object_or_404(Car,id=id)
    return render(request,'car_detail.html',{'car':car})

def add_car(request):
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('cars')
    else:
        form = CarForm()

    return render(request,'add_car.html',{'form':form})

def compare(request):
    cars = Car.objects.all()
    
    car1 = request.GET.get('car1')
    car2 = request.GET.get('car2')

    car1_data = None
    car2_data = None

    if car1 and car2:
        car1_data = Car.objects.get(id=car1)
        car2_data = Car.objects.get(id=car2)
        
    return render(request,'compare.html',{
        'cars':cars,
        'car1':car1_data,
        'car2':car2_data
    })



def testdrive(request):

    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        car_name = request.POST['car']
        date = request.POST['date']
        time = request.POST['time']

        TestDrive.objects.create(
            name=name,
            email=email,
            phone=phone,
            car_name=car_name,
            date=date,
            time=time
        )

        
        return render(request,'testdrive.html',{'success':True})
       
    return render(request,'testdrive.html')