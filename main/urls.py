from django.urls import path
from . import views

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

]
