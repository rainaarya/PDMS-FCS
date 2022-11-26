from django.shortcuts import render
from .forms import ProductPaymentForm
import razorpay
from .models import Product
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from website import settings
from django.db.models import Q

#user_product_dict = dict()


def Product_payment(request):
    if request.method == "POST":
        price = settings.product_price_dict[request.POST.get('id_of_product')]
        quantity = int(request.POST.get('quantity'))
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
                username=User.objects.get(id=request.user.id).username,
                name=name,
                amount=amount,
                order_id=order_id
            )
            cold_Product.save()
            response_payment['name'] = name
            #response_payment['email'] = User.objects.get(id=request.user.id).email

            # form = ProductPaymentForm(request.POST or None)
            #print(User.objects.get(id=request.user.id).email)

            # if(User.objects.get(id=request.user.id).username in user_product_dict.keys()):
            #     user_product_dict[User.objects.get(id=request.user.id).username].append(cold_Product)
            # else:
            #     user_product_dict[User.objects.get(id=request.user.id).username] = []
            #     user_product_dict[User.objects.get(id=request.user.id).username].append(cold_Product)

            return render(request, 'abc/Product_payment.html', {'payment': response_payment, 'email': request.user})


    return render(request, 'abc/store.html')

@csrf_exempt
def payment_status(request):
    response = request.POST
    params_dict = {
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature': response['razorpay_signature']
    }
    # prod=Product.objects.get(order_id=params_dict['razorpay_order_id'])
    # prod.razorpay_payment_id=params_dict['razorpay_payment_id']
    # prod.paid=True
    # prod.save()
    #print(f"Payment id is {response['razorpay_payment_id']}")


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


def refund(request):
    if request.method == "POST":

        # get product from database
        prod = Product.objects.get(order_id=request.POST.get('prod'))
        
        print(prod.order_id)


        # for i in range(len(user_product_dict[User.objects.get(id=request.user.id).username])):
        #     if(user_product_dict[User.objects.get(id=request.user.id).username][i].order_id == request.POST.get('prod')):
        #         product = user_product_dict[User.objects.get(id=request.user.id).username][i]

        #print(product.order_id)
        # get payment_id from order_id razorpay
        client = razorpay.Client(auth=("rzp_test_FSmJq64QVMJZoT" , "2JB2coseLqjG7yWsniKIHs4Y"))
        details = client.order.fetch(prod.order_id)
        #details = client.order.fetch(product.order_id)
        # print(details)
        product_order=Product.objects.get(order_id=details['id'])
        payment_id = product_order.razorpay_payment_id

        client.payment.refund(payment_id,{
        "amount": details['amount'],
        "speed": "optimum",
        "receipt": "Receipt No. 31"
        })

        #update to paid = 0
        product_order.paid = False
        product_order.save()

        return render(request, 'abc/refund_redirect.html', {'prod': details['id']})

    else:
        path = ""
        # if(User.objects.get(id=request.user.id).username in user_product_dict.keys()):
        #     path = 'abc/refund.html'
        # else:
        #     path = 'abc/refund_no_prod.html'

        #Product.objects.filter(lastname__icontains='User.objects.get(id=request.user.id).username').values()

        if(Product.objects.filter(username=User.objects.get(id=request.user.id).username, paid = True)!=None):
            path = 'abc/refund.html' 
            # find all products of user
            products = Product.objects.filter(username=User.objects.get(id=request.user.id).username, paid = True)

            
            return render(request, path, {'products': products})
        else:
            path = 'abc/refund_no_prod.html'
            return render(request, path, {'products': []})


