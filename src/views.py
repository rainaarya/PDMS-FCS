from django.shortcuts import render
from .forms import ProductPaymentForm
from django.contrib.auth.models import User, Group
from .models import Product
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from website import settings
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from main.models import Profile
import razorpay
import pyotp
import random
import string
import base64


def make_secret_key(random_string):
    return str(datetime.date(datetime.now())) + random_string

def Product_payment(request):
    
    if request.method == 'GET':
        form = ProductPaymentForm()
        return render(request, 'abc/store.html')
    
    if request.method == "POST":
        price = settings.product_price_dict[request.POST.get('id_of_product')]
        quantity = int(request.POST.get('quantity'))
        print(price, quantity)
        name = settings.product_price_dict[request.POST.get('id_of_product')]
        amount = price*quantity*100

        # create Razorpay client
        client = razorpay.Client(auth=("rzp_test_FSmJq64QVMJZoT" , "2JB2coseLqjG7yWsniKIHs4Y"))

        # create order
        response_payment = client.order.create(dict(amount=amount,currency='INR'))

        order_id = response_payment['id']
        order_status = response_payment['status']

        if order_status == 'created':
            cold_Product = Product(
                name=name,
                amount=amount,
                order_id=order_id
            )
            cold_Product.save()
            response_payment['name'] = name

            # form = ProductPaymentForm(request.POST or None)
            user = request.user
            print("\n")
            print(user.is_authenticated,"\n")
            request.session['otp_user_id'] = user.id
            email = User.objects.get(id=request.user.id).email
            secret_key = make_secret_key(''.join(random.choices(string.ascii_uppercase + string.digits, k=10))) + user.email
            encoded_key = base64.b32encode(secret_key.encode())
            one_time_password = pyotp.TOTP(encoded_key, interval=300)  
            subject = 'Validating OTP'
            message = '\nThe 6 digit OTP is: ' + str(
                one_time_password .now()) + '\n\nThis is a system-generated response for your OTP. Please do not reply to this email.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)
            request.session['otp_key'] = secret_key
            request.session['response_payment'] = response_payment
            return redirect('/otp_payment')
            
            
            
            # return render(request, 'abc/Product_payment.html', {'payment': response_payment})

def otp_payment(request):
    if not(request.user.is_authenticated):
        return HttpResponse("<h1>Error</h1><p>Bad Requesttt</p>")

    if 'otp_user_id' not in request.session.keys():
        return HttpResponse("<h1>Error</h1><p>Bad Request</p>")

    if request.method == "GET":
        user = User.objects.get(id=request.session['otp_user_id'])
        args = {"email": user.email}
        return render(request, "registration/otp.html", args)
    
    elif request.method == "POST":
        secret_key = request.session['otp_key']
        encoded_key = base64.b32encode(secret_key.encode())
        request.session.pop('otp_key')
        one_time_password = pyotp.TOTP(encoded_key, interval=300)
        user = User.objects.get(id=request.session['otp_user_id'])
        request.session.pop('otp_user_id')
        response_payment = request.session['response_payment']
        request.session.pop('response_payment')
        if one_time_password.verify(request.POST["otp"]):
            #login(request, user)
            return render(request, 'abc/Product_payment.html', {'payment': response_payment})
        else:
            # delete the user and profile from the database
            user_profile = Profile.objects.get(user_id=user.id)
            user_profile.delete()
            user.delete()
            return HttpResponse(f"<h1>Error</h1><p> OTP was wrong or has been expired </p><p><a href='{'/sign-up'}'>Try again</a></p>")
    else:
        return HttpResponse("<h1>Error</h1><p>Bad Request</p>")    

@csrf_exempt
def payment_status(request):
    response = request.POST
    params_dict = {
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    # client instance
    client = razorpay.Client(auth=("rzp_test_FSmJq64QVMJZoT" , "2JB2coseLqjG7yWsniKIHs4Y"))

    try:
        status = client.utility.verify_payment_signature(params_dict)
        cold_Product = Product.objects.get(order_id=response['razorpay_order_id'])
        cold_Product.razorpay_payment_id = response['razorpay_payment_id']
        cold_Product.paid = True
        cold_Product.save()
        return render(request, 'abc/payment_status.html', {'status': True})
    except:
        return render(request, 'abc/payment_status.html', {'status': False})
