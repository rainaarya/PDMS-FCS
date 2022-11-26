from django.urls import path
from .views import Product_payment, payment_status, refund

urlpatterns = [
    path('payment', Product_payment, name='Product-payment'),
    path('payment-status', payment_status, name='payment-status'),
    path('refund', refund, name='refund')
]
