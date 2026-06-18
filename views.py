import random
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from usernametoemail.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from email_validator import validate_email, EmailNotValidError

# Create your views here.
def index(request):
    return render(request,'home.html')





@login_required
def calculate_emi(request):

    context = {
        'amount': 400000,
        'months': 48,
        'annual_rate': 12.0,
        'emi': 10534
    }

    if request.method == 'POST':
        # annual_rate_input = request.POST.get('annual_rate', '10')
        months_input = request.POST.get('months', '48')
        amount_input = request.POST.get('amount', '500000')

        # Track previous values to know what changed
        old_months_input = request.POST.get('old_months', months_input)
        old_amount_input = request.POST.get('old_amount', amount_input)

        try:
            n = int(months_input)
            principal = int(amount_input)
            # annual_rate = float(annual_rate_input)

            old_n = int(old_months_input)
            old_principal = int(old_amount_input)


            if n != old_n:

                if n == 12:
                    # principal = min(principal, 200000)
                      principal=min(principal,50000)
                elif n == 24:
                    # principal = min(principal, 350000)
                    principal=min(principal,100000)
                elif n == 36:
                    # principal = min(principal, 425000)
                    principal=min(principal,200000)
                elif n == 48:
                    # principal = min(principal, 500000)
                    principal = min(principal, 400000)


            elif principal != old_principal:
                if  old_n==48:
                    principal=principal

                elif old_n==36:
                    if 50000<=principal<=200000:
                        n=36
                    else:
                        n=48
                elif old_n==24:
                    if 50000<principal<=100000:
                        n=24
                    elif 100000<principal<=200000:
                        n=36
                    else:
                        n=48
                elif old_n==12:
                    if principal<=50000:
                        n=12
                    elif 50000<principal<=100000:
                        n=24
                    elif 100000<principal<=200000:
                        n=36
                    else:
                        n=48




            annual_rate=12
            r = (annual_rate / 12) / 100
            if r > 0:
                emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
            else:
                emi = principal / n

            context = {
                'emi': round(emi),
                'amount': principal,
                'months': n,
                # 'annual_rate': annual_rate
            }

        except (ValueError, ZeroDivisionError):
            messages.error(request, "Invalid inputs provided.")

    return render(request, 'emi.html', context)


def hello(request):
    return HttpResponse("Hello, world.")

def register(request):
    if request.method == "POST":
        email = request.POST.get("email","")

        # try:
        #     # 1. Validate email structure and deliverability
        #     email_info = validate_email(email, check_deliverability=True)
        #     email = email_info.normalized
        try:

            email_info = validate_email(email, check_deliverability=True)


            if email_info.mx_fallback_type is not None:
                messages.error(request, "This domain does not have a valid mail server (MX record).")
                return render(request, 'register.html')

            email = email_info.normalized

        except EmailNotValidError:
            messages.error(request, "This email domain does not exist or is invalid.")
            return render(request, 'register.html')


        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "User already exists.")
            return redirect('/login/')


        otp = str(random.randint(100000, 999999))
        send_mail(
            subject='verification email from nki bank',
            message=f'Your verification code is {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )


        request.session['user_mail'] = email
        request.session['generated_otp'] = otp
        request.session.set_expiry(300)

        return redirect('/verify/')

    return render(request, 'register.html')


def verify(request):
    if request.method == "POST":
        saved_otp = request.session.get('generated_otp')
        user_otp = request.POST.get('otp')

        if saved_otp is None:
            messages.error(request, "Please request a new OTP.")
            return redirect('/register/')

        if saved_otp == user_otp:

            request.session.pop('generated_otp', None)


            request.session['email_verified'] = True

            messages.success(request, 'Email verified successfully! Please set your password.')
            return redirect('/set_newpassword/')
        else:
            messages.error(request, 'Verification failed. Wrong OTP.')
            return redirect('/verify/')

    return render(request, 'verify.html')


def set_newpassword(request):

    session_email = request.session.get('user_mail')
    is_verified = request.session.get('email_verified')

    if not session_email or not is_verified:
        messages.error(request, "Unauthorized access. Please register and verify your email first.")
        return redirect('/register/')

    if request.method == "POST":
        password = request.POST.get('password',"")
        confirm_password = request.POST.get('confirm_password',"")


        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'set_newpassword.html')


        try:
            validate_password(password,user=CustomUser(email=session_email)) #idhar mene baad me change kiya he
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'set_newpassword.html')


        CustomUser.objects.create_user(email=session_email, password=password)


        request.session.flush()

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('/login/')

    return render(request, 'set_newpassword.html')

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not CustomUser.objects.filter(email=email).exists():
            messages.error(request,"user does not exist")
            return redirect('/register/')

        user=authenticate(username=email,password=password)
        if user is None:
            messages.error(request,"your password is incorrect")
            return render(request, 'login.html')
        else:
            login(request,user)
            return redirect('/emi/')
    return render(request, 'login.html')

def logout_page(request):
    logout(request)
    messages.success(request,'You are Successfully logout')
    return redirect('/login/')
def forgot_password(request):
    if request.method == 'POST':
        email=request.POST.get('email',"")
        # request.session['user_email']=email
        try:

            email_info2 = validate_email(email, check_deliverability=True)
            email = email_info2.normalized  # Automatically cleans and lowercases it
        except EmailNotValidError:
            messages.error(request, "This email domain does not exist or is invalid.")
            return render(request, 'forgot_password.html')
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(request,"user does not exist")
            return redirect('/register/')


        else:
            otp = str(random.randint(100000, 999999))
            send_mail(subject='verification email from nki bank',
                      message=f'This is an instant test email sent from the Django server {otp}',
                      from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[email],
                      fail_silently=False, )
            request.session['forgot_user_email']=email
            request.session['forgot_generated_otp']=otp
            request.session.set_expiry(300)
            return redirect('/verify_forgot/')
    return render(request,'forgot_password.html')
def verify_forgot(request):
    if request.method=='POST':
        if_saved_otp=request.session.get('forgot_generated_otp')
        if_user_otp=request.POST.get('otp')
        if if_saved_otp is None:
            return redirect('/forgot_password/')
        elif if_user_otp==if_saved_otp:
            email = request.session.get('forgot_user_email')
            user=CustomUser.objects.filter(email=email).first()

            if user:
              request.session.pop('forgot_generated_otp', None)
              request.session['forgot_otp_verified']=True
              request.session['forgot_user_id']=user.id

              messages.success(request,'verification successful')
              # return redirect(f'/set_password/{user.id}')
              return redirect('/set_password/')
            else:
                messages.error(request, 'Session corrupted. Please start over.')
                return redirect('/forgot_password/')

        else:
            messages.error(request,'verification failed')
            return redirect('/forgot_password/')
    return render(request,'verify_forgot.html')


def set_password(request):

    # user = get_object_or_404(CustomUser, id=id)
    is_verified1=request.session.get('forgot_otp_verified')
    user_id=request.session.get('forgot_user_id')

    if not is_verified1 or not user_id:
        messages.error(request,'unauthorized access,please verify your otp first')
        return redirect('/forgot_password/')

    user=get_object_or_404(CustomUser,id=user_id)
    if request.method == 'POST':
        password = request.POST.get('password',"")
        confirm_password = request.POST.get('confirm_password',"")
        if not password or not confirm_password:
            messages.error(request, "Password fields cannot be empty.")
            return render(request, 'set_password.html', {'user': user})

        if password!=confirm_password:
            messages.error(request,'password do not match')
            return render(request, 'set_password.html', {'user': user})
        try:
                # validate_password(password)
            validate_password(password,user=user)

        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'set_password.html', {'user': user})
        user.set_password(password)
        user.save()
        request.session.pop('forgot_otp_verified', None)
        request.session.pop('forgot_user_id', None)
        request.session.pop('forgot_user_email',None)

        messages.success(request,'your password is set')
        return redirect('/login/')


    return render(request, 'set_password.html', {'user': user})











################################################################








#####old register and verify with email and password then takes user to verification page
# def register(request):
#     if request.method=="POST":
#         email=request.POST.get("email")
#         password=request.POST.get("password")
#         try:
#
#             email_info = validate_email(email, check_deliverability=True)
#             email = email_info.normalized
#         except EmailNotValidError:
#             messages.error(request, "This email domain does not exist or is invalid.")
#             return render(request, 'register.html')
#         # user=CustomUser(email=email,password=password)
#         if CustomUser.objects.filter(email=email).exists():
#            messages.error(request,"user already exists")
#            return redirect('/login/')
#         else:
#             try:
#
#                 validate_password(password)
#             except ValidationError as e:
#
#                 for error in e.messages:
#                     messages.error(request, error)
#
#                 return render(request, 'register.html')
#
#             otp=str(random.randint(100000,999999))
#             send_mail(subject='verification email from nki bank',
#                 message=f'This is an instant test email sent from the Django server {otp}',
#                 from_email=settings.EMAIL_HOST_USER,
#                 recipient_list=[email],
#                 fail_silently=False,)
#             request.session['user_mail']=email
#             request.session['generated_otp']=otp
#             request.session['password']=password
#             request.session.set_expiry(300)
#             return redirect('/verify/')
#
#     return render(request,'register.html')
#
# def verify(request):
#     if request.method=="POST":
#         saved_otp=request.session.get('generated_otp')
#         user_otp=request.POST.get('otp')
#         # user_email=request.POST.get("email")
#
#         if saved_otp is None:
#             messages.error(request, "please request a new otp :")
#             return redirect('/register/')
#         elif saved_otp==user_otp:
#
#             session_email=request.session.get('user_mail')
#             session_password=request.session.get('password')
#             if session_email and session_password:
#                CustomUser.objects.create_user(email=session_email, password=session_password)
#                request.session.pop('generated_otp', None)
#                request.session.pop('user_mail', None)
#                request.session.pop('password', None)
#
#                messages.success(request,'verification successful')
#                return redirect('/login/')
#             else:
#
#               messages.error(request, 'Registration data lost. Please register again.')
#               return redirect('/register/')
#
#
#         else:
#
#             messages.error(request, 'Verification failed. Wrong OTP.')
#
#             return redirect('/verify/')
#
#     return render(request,'verify.html')




# @login_required
# def calculate_emi(request):
#     context = {
#         'amount': 500000,
#         'months': 48,
#         'annual_rate': 10.0,
#         'emi': 12681.29
#     }
#
#     if request.method == 'POST':
#         annual_rate_input = request.POST.get('annual_rate', '10')
#         months_input = request.POST.get('months', '48')
#         amount_input = request.POST.get('amount', '500000')
#
#         try:
#             n = int(months_input)
#             principal = int(amount_input)
#             annual_rate = float(annual_rate_input)
#
#
#             # if n == 12:
#             #     if principal > 200000:
#             #         principal = 200000
#             # elif principal<=200000:
#             #     n=12
#             # elif n == 24:
#             #     if principal > 350000 :
#             #         principal = 350000
#             # elif 200000<principal<=350000:
#             #     n=24
#             # elif n == 36:
#             #     if principal > 425000 :
#             #         principal = 425000
#             # elif 350000<principal<=425000:
#             #     n=48
#             # elif n == 48:
#             #     if principal > 500000 :
#             #         principal = 500000
#             # elif 425000<principal<=500000:
#             #     n=48
#             if n == 12:
#                 principal = min(principal, 200000)
#             elif n == 24:
#                 principal = min(principal, 350000)
#             elif n == 36:
#                 principal = min(principal, 425000)
#             elif n == 48:
#                 principal = min(principal, 500000)
#
#                 # Step B: Enforce Minimum Tenure based on selected/adjusted Amount
#             if principal <= 200000:
#                 n = 12
#             elif 200000 < principal <= 350000:
#                 n = 24
#             elif 350000 < principal <= 425000:
#                 n = 36
#             elif 425000 < principal<=500000:
#                 n=48
#
#             r = (annual_rate / 12) / 100
#             if r > 0:
#                 emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
#             else:
#                 emi = principal / n
#
#             context = {
#                 'emi': round(emi, 2),
#                 'amount': principal,
#                 'months': n,
#                 'annual_rate': annual_rate
#             }
#
#         except (ValueError, ZeroDivisionError):
#             messages.error(request, "Invalid inputs provided.")
#
#     return render(request, 'emi.html', context)