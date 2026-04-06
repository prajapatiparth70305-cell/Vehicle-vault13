from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()
from .forms import UserSignupForm,UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail,EmailMultiAlternatives, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from .models import Car,Purchase,Invoice,Cart,Notification,EMIHistory,TestDrive
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
    "🚗 Welcome to Vehicle Vault - Verify Your Account",
    f"""
Hello {user.email},

🎉 Congratulations! Your signup is successful.

Welcome to Vehicle Vault 🚗

To verify your account, use the OTP below:

🔐 OTP: {otp}

⏱ This OTP is valid for 30 seconds.

⚠️ Do not share this OTP with anyone.

Thank you,
Vehicle Vault Team
""",
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

    purchased_cars = Purchase.objects.filter(
        user=request.user,
        is_insurance=False
    ).count()

    insurance_active = Purchase.objects.filter(
        user=request.user,
        is_insurance=True
    ).count()

    unread_count = request.user.notifications.filter(is_read=False).count()

    # 🔥 EMI DASHBOARD LOGIC
    emis = EMIHistory.objects.all()

    total_paid = 0
    total_due = 0
    overdue = 0

    today = timezone.now().date()

    for emi in emis:
        if emi.next_due_date:
            if today > emi.next_due_date:
                overdue += 1
                total_due += emi.amount
            elif emi.next_due_date - today <= timedelta(days=3):
                total_due += emi.amount
            else:
                total_paid += emi.amount

    return render(request, 'dashboard.html', {
        'total_cars': total_cars,
        'purchased_cars': purchased_cars,
        'insurance_active': insurance_active,
        'unread_count': unread_count,

        # 🔥 EMI DATA
        'total_paid': total_paid,
        'total_due': total_due,
        'overdue': overdue,
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

    # ✅ EMAIL SEND KARO
    subject = "Payment Successful 🚗"
    message = f"""
Hello {request.user.email},

Your payment has been completed successfully.

Car: {car.name}
Amount Paid: ₹{amount}

You can check your purchase history anytime.

Thank you for choosing This Car 🚗
"""

    # ⚠️ Ensure email exists
    if request.user.email:
        send_mail(
            subject,
            message,
            'your_email@gmail.com',  # sender email
            [request.user.email],   # receiver
            fail_silently=False,
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



def testdrive(request):
    cars = Car.objects.all()

    if request.method == "POST":
        car_id = request.POST.get('car')
        pickup_location = request.POST.get('location')
        date = request.POST.get('date')
        time = request.POST.get('time')

        car = Car.objects.get(id=car_id)

        # Save in DB
        TestDrive.objects.create(
            user=request.user,
            car=car,
            pickup_location=pickup_location,
            date=date,
            time=time
        )
        create_notification(
            request.user,
            f"{car.name} added successfully 🚗",
            "success"
        )

        # EMAIL SEND
        subject = "🚗 Test Drive Confirmation"
        from_email = "your_email@gmail.com"
        to_email = [request.user.email]

        html_content = render_to_string('testdrive_email.html', {
            'user': request.user,
            'car': car,
            'pickup_location': pickup_location,
            'date': date,
            'time': time
        })

        msg = EmailMultiAlternatives(subject, "", from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return redirect('cars')

    return render(request, 'testdrive.html', {'cars': cars})


    

@login_required

def add_to_cart(request, id):
    car = get_object_or_404(Car, id=id)  

    Cart.objects.create(
        user=request.user,
        car=car
    )

    return redirect('cart_page')

def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)

    total_price = sum(item.car.price for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


def remove_from_cart(request, id):
    item = get_object_or_404(Cart, id=id)
    item.delete()
    return redirect('cart_page')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email__iexact=email.strip())

            # ✅ Save BOTH email + user id
            request.session['reset_user'] = user.id
            request.session['reset_email'] = user.email

            return redirect('reset_password')

        except User.DoesNotExist:
            messages.error(request, "Email not registered")

    return render(request, 'password/forgot_password.html')


def reset_password(request):
    if 'reset_user' not in request.session:
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')
        email = request.POST.get('email')  # 👈 user se dubara email lo

        # ✅ Check email matches session email
        if email != request.session.get('reset_email'):
            messages.error(request, "Email does not match")
            return redirect('reset_password')

        if password == confirm:
            user = User.objects.get(id=request.session['reset_user'])
            user.set_password(password)
            user.save()

            del request.session['reset_user']
            del request.session['reset_email']

            messages.success(request, "Password updated successfully")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match")

    return render(request, 'password/reset_password.html')

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

    # 🔥 PLAN BASED EXPIRY
    if plan == "Basic":
        expiry = timezone.now() + timedelta(days=365)
    elif plan == "Standard":
        expiry = timezone.now() + timedelta(days=365*2)
    elif plan == "Premium":
        expiry = timezone.now() + timedelta(days=365*3)
    else:
        expiry = timezone.now()

    # 🔥 SAVE
    purchase = Purchase.objects.create(
        user=request.user,
        car=car,
        amount=amount,
        status="Paid",
        is_insurance=True,
        insurance_plan=plan,
        expiry_date=expiry
    )

    create_notification(
        request.user,
        f"Insurance purchased for {car.name} ({plan}) 🛡️",
        "success"
    )

    # 🔥 EMAIL (with expiry)
    subject = "Insurance Purchase Successful 🚗"
    message = f"""
Hello {request.user.email},

Your insurance has been successfully purchased!

Car: {car.name}
Plan: {plan}
Amount Paid: ₹{amount}
Expiry Date: {expiry.strftime('%d %b %Y')}

Drive safe! 🛡️
Vehicle Vault Team
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=False
    )

    return render(request, 'insurance/success.html', {
        'user': request.user,
        'car': car,
        'plan': plan,
        'amount': amount,
        'expiry': expiry
    })

@login_required
def insurance_history(request):
    purchases = Purchase.objects.filter(
        user=request.user,
        is_insurance=True
    )

    # 🔥 CHECK EXPIRED
    for p in purchases:
        if p.expiry_date and p.expiry_date < timezone.now().date():
            if not p.is_expired:
                p.is_expired = True
                p.status = "Expired"
                p.save()

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
    return redirect('notifications')

def emi_page(request):
    car_name = request.GET.get("car")
    price = request.GET.get("price")

    # ✅ SAVE IN SESSION (IMPORTANT)
    request.session['car_name'] = car_name

    return render(request, "emi/emi.html", {
        "car_name": car_name,
        "price": price
    })

def success_page(request):
    payment_id = request.GET.get("payment_id")
    amount = request.GET.get("amount")
    total_emi = request.GET.get("total_emi")

    car_name = request.session.get("car_name")

    if payment_id:
        emi = EMIHistory.objects.create(
            payment_id=payment_id,
            amount=amount,
            car_name=car_name,
            total_emi=int(total_emi),
            paid_emi=1,
            next_due_date=timezone.now().date() + timedelta(days=30)  
        )

        create_notification(
            request.user,
            f"Your emi purchased successfully 🎉",
            "success"
        )

        # EMAIL SAME रहेगा
        if request.user.is_authenticated:
            subject = "EMI Payment Successful 💳"
            message = f"""
Hello {request.user.email},

Your EMI payment has been successfully completed!

Car: {car_name}
Payment ID: {payment_id}
Amount Paid: ₹{amount}
Next Due Date: {emi.next_due_date}

Thank you 🚗
"""
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False
            )

    return render(request, "emi/success.html")



def history_page(request):
    data = EMIHistory.objects.all().order_by('-id')

    return render(request, "emi/history.html", {"data": data})


# DELETE
def delete_history(request, id):
    item = EMIHistory.objects.get(id=id)
    item.delete()
    return redirect('/core/history/')


# VIEW SINGLE
def view_history(request, id):
    data = EMIHistory.objects.get(id=id)
    return render(request, "emi/view.html", {"item": data})


def next_emi(request, id):
    client = razorpay.Client(auth=("rzp_test_SRMYrgg9z1ynoY", "H8Fzo9bxZA2Kh5LmFFiToIb3"))

    emi = EMIHistory.objects.get(id=id)

    request.session['car_name'] = emi.car_name

    amount = emi.amount * 100

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    return render(request, "emi/emipay.html", {
        "payment": payment,
        "emi": emi,
        "razorpay_key": "rzp_test_SRMYrgg9z1ynoY"
    })


@login_required
def download_invoice(request, id):
    """Generate and download invoice as PDF"""
    purchase = get_object_or_404(Purchase, id=id)
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#333333'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    normal_style = styles['Normal']
    
    # Add title
    elements.append(Paragraph("🧾 INVOICE", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Add user details
    details_data = [
        ['User Email:', purchase.user.email],
        ['Car Name:', purchase.car.name],
        ['Insurance Plan:', purchase.insurance_plan],
        ['Date:', purchase.date.strftime('%d %b %Y')],
    ]
    
    details_table = Table(details_data, colWidths=[2*inch, 3*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(details_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add invoice items table
    invoice_data = [
        ['Description', 'Amount'],
        [f'{purchase.insurance_plan} Insurance for {purchase.car.name}', f'₹ {purchase.amount}'],
    ]
    
    invoice_table = Table(invoice_data, colWidths=[3.5*inch, 1.5*inch])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('PADDING', (0, 1), (-1, -1), 12),
    ]))
    
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Add total
    total_style = ParagraphStyle(
        'Total',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        alignment=2  # Right
    )
    elements.append(Paragraph(f"<b>Total: ₹ {purchase.amount}</b>", total_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Return as download
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{purchase.id}.pdf"'
    return response


