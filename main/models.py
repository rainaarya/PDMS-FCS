from tkinter import N
from django.db import models
from django.contrib.auth.models import User
from yaml import DocumentStartEvent


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title + "\n" + self.description

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # create attribute for role with choices
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('healthcarepro', 'Healthcare Professional'),
        ('hospital', 'Hospital'),
        ('pharmacy', 'Pharmacy'),
        ('insurance', 'Insurance Firm')
    )
    role = models.CharField(max_length=13, choices=ROLE_CHOICES, default='patient')
    document1=models.FileField(upload_to='documents/', null=True, blank=True)
    document2=models.FileField(upload_to='documents/', null=True, blank=True)
    organisation_name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image1 = models.ImageField(upload_to='images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='images/', null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    contact = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.role