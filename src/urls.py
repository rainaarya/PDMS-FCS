from django.urls import path
from .views import Product_payment, payment_status, refund, otp_payment

urlpatterns = [
    path('payment', Product_payment, name='Product-payment'),
    path('payment-status', payment_status, name='payment-status'),
    path('otp_payment', otp_payment, name='otp_payment'),
    path('refund', refund, name='refund')
]
