from django.shortcuts import render
from .forms import ProductPaymentForm
import razorpay
from .models import Product
from django.views.decorators.csrf import csrf_exempt
from website import settings

def Product_payment(request):
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
            return render(request, 'abc/Product_payment.html', {'payment': response_payment})

    form = ProductPaymentForm()
    return render(request, 'abc/store.html')

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
