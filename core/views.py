from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()
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
import razorpay,random
from django.utils import timezone
from datetime import timedelta




def home(request):
    return render(request,'home.html')

def signup(request):
    if request.method =="POST":
      form = UserSignupForm(request.POST or None)
      if form.is_valid():
        # save the new user first
        user = form.save()
          # ✅ OTP generate
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.is_verified = False
        user.save()

            # ✅ Email send
        send_mail(
                "Your OTP Code",
                f"Your OTP is {otp}",
                "your@email.com",
                [user.email],
            )

            # ❌ remove this
            # return redirect('login')

            # ✅ add this
        request.session['email'] = user.email
        return redirect('verify_otp')

    else:
        form = UserSignupForm()

    return render(request, 'core/signup.html', {'form': form})

def verify_otp(request):
    email = request.session.get('email')

    if request.method == "POST":
        otp = request.POST.get("otp")

        user = User.objects.get(email=email)

        if user.otp == otp:
            user.is_verified = True
            user.otp = None
            user.save()

            return redirect('login')  # ✅ ab login open hoga
        else:
            return render(request, 'core/verify.html', {'error': 'Invalid OTP'})

    return render(request, 'core/verify.html')

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
@login_required
def payment_success(request, car_id):
    amount = request.GET.get('amount')

    # 🔥 database me save karo
    Purchase.objects.create(
        user=request.user,
        car_id=car_id,
        amount=amount,
        status="Paid"
    )
    
    return render(request, 'payment_success.html', {
        'amount': amount
    })



def purchase_history(request):
    purchases = Purchase.objects.filter(user=request.user)
  

    return render(request, 'purchase_history.html', {
        'purchases': purchases,
        
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





def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            request.session['reset_user'] = user.id
            return redirect('reset_password')
        except User.DoesNotExist:
            messages.error(request, "Email not found")

    return render(request, 'forgot_password.html')


def reset_password(request):
    if 'reset_user' not in request.session:
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password == confirm:
            user = User.objects.get(id=request.session['reset_user'])
            user.set_password(password)
            user.save()

            del request.session['reset_user']
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match")

    return render(request, 'reset_password.html')

