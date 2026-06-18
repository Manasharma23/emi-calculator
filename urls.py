from django.contrib import admin
from django.urls import path,include
from usernametoemail import views
urlpatterns = [

    path('',views.index,name='index'),
    path('hello/',views.hello,name='hello'),
    path('emi/',views.calculate_emi,name='emi'),
    path('register/',views.register,name='register'),
    path('verify/',views.verify,name="verify"),
    path('login/',views.login_page,name="login_page"),
    path('logout/',views.logout_page,name="logout_page"),
    path('forgot_password/',views.forgot_password,name="forgot_password"),
    path('verify_forgot/',views.verify_forgot,name="verify_forgot"),
    path('set_password/',views.set_password,name="set_password"),

    path('set_newpassword/',views.set_newpassword,name="set_newpassword"),


]
