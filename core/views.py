from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()
from .forms import UserSignupForm,UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail,EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Car,Purchase,Invoice,Cart,Notification,EMIHistory
from .forms import CarForm
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


@login_required
def dashboard(request):

    total_cars = Car.objects.count()

   
    purchased_cars = Purchase.objects.filter(user=request.user, is_insurance=False).count()

  
    insurance_active = Purchase.objects.filter(user=request.user, is_insurance=True).count()

   
    unread_count = request.user.notifications.filter(is_read=False).count()

    return render(request, 'dashboard.html', {
        'total_cars': total_cars,
        'purchased_cars': purchased_cars,
        'insurance_active': insurance_active,
        'unread_count': unread_count
    })

def user_logout(request):
    logout(request)
    messages.success(request,"You have successfully logged out.")
    return redirect('login')

def cars(request):
    cars = Car.objects.all()

    search_query = request.GET.get('search')

    if search_query:
        cars = cars.filter(name__icontains=search_query)

    return render(request, 'cars.html', {
        'cars': cars,
        'search_query': search_query
    })


def delete_car(request, id):
    car = get_object_or_404(Car, id=id)
    car.delete()
    return redirect('cars')

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

        car = Car.objects.create(
            name=name,
            brand=brand,
            number=number,
            mileage=mileage,
            fuel_type=fuel_type,
            price=price,
            image=image,
        )

        create_notification(
            request.user,
            f"{car.name} added successfully 🚗",
            "success"
        )

        return redirect('cars')

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

    car = Car.objects.get(id=car_id)

    Purchase.objects.create(
        user=request.user,
        car=car,
        amount=amount,
        status="Paid"
    )

    
    create_notification(
        request.user,
        f"You purchased {car.name} successfully 🎉",
        "success"
    )

    return render(request, 'payment_success.html', {
        'amount': amount,
        'car': car
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
    return redirect('cart_page')





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

def insurance_page(request, car_id):
    car = Car.objects.get(id=car_id)

    # 🔥 Price based 3 plans
    basic = int(car.price * 0.03)      # 3%
    standard = int(car.price * 0.06)   # 6%
    premium = int(car.price * 0.10)    # 10%

    return render(request, 'insurance/insurance_page.html', {
        'car': car,
        'basic': basic,
        'standard': standard,
        'premium': premium
    })


def buy_insurance(request, car_id):
    if request.method == "POST":
        plan = request.POST.get('plan')
        amount = int(request.POST.get('amount')) * 100

        client = razorpay.Client(auth=("rzp_test_SRMYrgg9z1ynoY", "H8Fzo9bxZA2Kh5LmFFiToIb3"))

        payment = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return render(request, 'insurance/payment.html', {
            'payment': payment,
            'plan': plan,
            'amount': amount // 100,
            'car_id': car_id,
            'razorpay_key': "rzp_test_SRMYrgg9z1ynoY"
        })
    
@login_required
def insurance_success(request, car_id):
    plan = request.GET.get('plan')
    amount = request.GET.get('amount')

    car = Car.objects.get(id=car_id)

    # 🔥 SAVE IN DATABASE
    Purchase.objects.create(
        user=request.user,
        car=car,
        amount=amount,
        status="Paid",
        is_insurance=True,
        insurance_plan=plan
    )

    create_notification(
        request.user,
        f"Insurance purchased for {car.name} ({plan}) 🛡️",
        "success"
    )

    return render(request, 'insurance/success.html', {
        'car': car,
        'plan': plan,
        'amount': amount
    })

@login_required
def insurance_history(request):
    purchases = Purchase.objects.filter(
        user=request.user,
        is_insurance=True
    )

    return render(request, 'insurance/history.html', {
        'purchases': purchases
    })

def insurance_invoice(request, id):
    purchase = Purchase.objects.get(id=id)

    return render(request, 'insurance/invoice.html', {
        'purchase': purchase
    })


@login_required
def delete_insurance(request, id):
    purchase = get_object_or_404(Purchase, id=id, user=request.user)

    purchase.delete()

    return redirect('insurance_history')

def create_notification(user, message, type='info'):
    Notification.objects.create(
        user=user,
        message=message,
        notification_type=type
    )

def get_notifications(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

def mark_as_read(request, id):
    notification = Notification.objects.get(id=id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required
def delete_notification(request, id):
    notification = get_object_or_404(Notification, id=id, user=request.user)
    notification.delete()
    return redirect('dashboard')

def emi_page(request):
    car_name = request.GET.get("car")
    price = request.GET.get("price")

    # ✅ SAVE IN SESSION (IMPORTANT)
    request.session['car_name'] = car_name

    return render(request, "core/emi.html", {
        "car_name": car_name,
        "price": price
    })


# SUCCESS PAGE (SAVE DATA)
def success_page(request):
    payment_id = request.GET.get("payment_id")
    amount = request.GET.get("amount")

    # ✅ ALWAYS GET FROM SESSION
    car_name = request.session.get("car_name")

    print("CAR NAME:", car_name)

    if payment_id:
        EMIHistory.objects.create(
            payment_id=payment_id,
            amount=amount,
            car_name=car_name
        )

    return render(request, "core/success.html")


# HISTORY PAGE
def history_page(request):
    data = EMIHistory.objects.all().order_by('-id')
    return render(request, "core/history.html", {"data": data})


# DELETE
def delete_history(request, id):
    item = EMIHistory.objects.get(id=id)
    item.delete()
    return redirect('/core/history/')


# VIEW SINGLE
def view_history(request, id):
    data = EMIHistory.objects.get(id=id)
    return render(request, "core/view.html", {"item": data})


# NEXT EMI PAYMENT
def next_emi(request, id):
    client = razorpay.Client(auth=("rzp_test_SRMYrgg9z1ynoY", "H8Fzo9bxZA2Kh5LmFFiToIb3"))

    emi = EMIHistory.objects.get(id=id)

    # ✅ SAVE AGAIN IN SESSION
    request.session['car_name'] = emi.car_name

    amount = emi.amount * 100

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    return render(request, "core/emipay.html", {
        "payment": payment,
        "emi": emi,
        "razorpay_key": "rzp_test_SRMYrgg9z1ynoY"
    })