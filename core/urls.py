from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.login_view, name='login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('cars/', views.cars, name='cars'),
    path('car/<int:id>/', views.car_detail, name='car_detail'), 
    path('buy-car/<int:id>/', views.buy_car, name='buy_car'),
    path('payment-success/<int:car_id>/', views.payment_success, name='payment_success'),
    path('purchase_history/',views.purchase_history,name='purchase_history'),
    path('delete_purchase/<int:id>/', views.delete_purchase,name='delete_purchase'),
    path("view_invoice/<int:id>/",views.invoice,name="view_invoice"),
    path('compare/' , views.compare,name='compare'),
    path('test-drive/', views.testdrive, name='test_drive'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('remove_from_cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('insurance/<int:car_id>/', views.insurance_page, name='insurance_page'),
    path('insurance/pay/<int:car_id>/', views.buy_insurance, name='buy_insurance'),
    path('insurance/success/<int:car_id>/', views.insurance_success, name='insurance_success'),
    path('insurance/history/', views.insurance_history, name='insurance_history'),
    path('insurance/invoice/<int:id>/', views.insurance_invoice, name='insurance_invoice'),
    path('insurance/delete/<int:id>/', views.delete_insurance, name='delete_insurance'),
    path('insurance/download-pdf/<int:id>/', views.download_invoice, name='download_invoice'),
    path('notifications/', views.get_notifications, name='notifications'),
    path('notification/read/<int:id>/', views.mark_as_read, name='mark_as_read'),
    path('notification/delete/<int:id>/', views.delete_notification, name='delete_notification'),
    path('emi', views.emi_page, name="emi"),
    path('success/', views.success_page),
    path('history/', views.history_page),
    path('delete-history/<int:id>/', views.delete_history,name='delete_history'),
    path('view-history/<int:id>/', views.view_history, name='view_history'),
    path('next-emi/<int:id>/', views.next_emi, name='next_emi'),
    
] 

  


