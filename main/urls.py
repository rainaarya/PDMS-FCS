from django.urls import path, include
from . import views
from src.views import Product_payment, payment_status, refund, otp_payment

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('patient', views.patient, name='patient'),
    path('insurance', views.insurance, name='insurance'),
    path('pharmacy', views.pharmacy, name='pharmacy'),
    path('hospital', views.hospital, name='hospital'),
    path('healthcarepro', views.healthcarepro, name='healthcarepro'),
    path('share/<int:receiver>', views.share, name='share'),
    path('otp', views.otp, name='otp'),    
    path('profile', views.profile_page, name='profile'),
    path('administrator', views.administrator, name='administrator'),
    path('store', Product_payment, name='store'),
    
]
