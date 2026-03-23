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
    path('add-car/' , views.add_car,name='add_car'),
    path('car/<int:id>/', views.car_detail, name='car_detail'), 
    path('buy-car/<int:id>/', views.buy_car, name='buy_car'),
    path('payment-success/<int:car_id>/', views.payment_success, name='payment_success'),
    path('purchase_history/',views.purchase_history,name='purchase_history'),
    path('delete_purchase/<int:id>/', views.delete_purchase,name='delete_purchase'),
    path("view_invoice/<int:id>/",views.invoice,name="view_invoice"),
    path('compare/' , views.compare,name='compare'),
    path('testdrive/',views.testdrive,name='testdrive'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('remove_from_cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('emi/<int:id>/', views.emi_calculator, name='emi_calculator'),  
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
]
    

  


