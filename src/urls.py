from django.urls import path
from . import views

urlpatterns = [
    path('payment', views.Product_payment, name='Product-payment'),
    path('payment-status', views.payment_status, name='payment-status'),
    path('otp_payment', views.otp_payment, name='otp_payment')
]
