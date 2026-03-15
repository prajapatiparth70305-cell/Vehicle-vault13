from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/',views.login_view,name="login"),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('cars/', views.cars, name='cars'),
    path('add-car/' , views.add_car,name='add_car'),
    path('car/<int:id>/', views.car_detail, name='car_detail'),
    path('compare/' , views.compare,name='compare'),
    path('testdrive/',views.testdrive,name='testdrive'),

    
    

  


]