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
from .models import Car,Purchase,Invoice,Cart
from .forms import CarForm, TestDrive
from django.http import HttpResponse
import razorpay
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
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        number = request.POST.get('number')
        mileage = request.POST.get('mileage')
        fuel_type = request.POST.get('fuel_type')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        

        Car.objects.create(
            name=name,
            brand=brand,
            number=number,
            mileage=mileage,
            fuel_type=fuel_type,
            price=price,
            image=image,
        
        )

        return redirect('cars')   # yaha redirect hona chahiye

    return render(request, 'add_car.html')



def buy_car(request, id):
    car = get_object_or_404(Car, id=id)

    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        client = razorpay.Client(auth=("rzp_test_SRMYrgg9z1ynoY", "H8Fzo9bxZA2Kh5LmFFiToIb3"))
        booking_amount=car.price
        amount = int(booking_amount*1)

        payment = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return render(request, 'payment.html', {
            'payment': payment,
            'car': car,
            'name': name,
            'phone': phone,
            'amount':booking_amount
            
        })

    return render(request, 'buy_car.html', {'car': car})



def payment_success(request):

    car_id = request.session.get('car_id')

    car = get_object_or_404(Car, id=car_id)

 
    payment_id = request.GET.get('payment_id', 'PAY123456')

    Purchase.objects.create(
        user=request.user,
        car=car,
        amount=car.price,
        status="Success",
        payment_id=payment_id
    )

    return redirect('purchase_history')


def purchase_history(request):

    purchases = Purchase.objects.filter(user=request.user)

    return render(request,"purchase_history.html",{
        "purchases":purchases
    })

def delete_purchase(request, id):
    purchase = Purchase.objects.get(id=id)  # small letter variable
    purchase.delete()
    return redirect('purchase_history')


def invoice(request,id):

    purchase = Purchase.objects.get(id=id)

    return render(request,"invoice.html",{
        "purchase":purchase
    })

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


def emi_calculator(request, id):
    car = Car.objects.get(id=id)
    return render(request, 'emi_page.html', {'car': car})

@login_required

def add_to_cart(request, id):
    car = get_object_or_404(Car, id=id)  

    Cart.objects.create(
        user=request.user,
        car=car
    )

    return redirect('cart_page')

@login_required
def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, 'cart.html', {'cart_items': cart_items})



def remove_from_cart(request, id):
    item = get_object_or_404(Cart, id=id)
    item.delete()
    return redirect('cars')

