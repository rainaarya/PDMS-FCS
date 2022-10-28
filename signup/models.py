from django.db import models
from phone_field import PhoneField
import datetime
import os

def get_file_path(request, filename):
    original_filename = filename
    nowTime = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S') 
    filename = "%s%s" % (nowTime, original_filename) 
    return os.path.join('uploads/', filename)


class approval(models.Model):
    email = models.EmailField('Email Address',null=False,blank=False,primary_key=True)
    document = models.FileField(upload_to='documents/')
    approve = models.BooleanField(default=False)
    
    def __str__(self):
        return self.email
    
    
class users(models.Model):
    name = models.CharField(max_length=100,null=False,blank=False)
    email = models.EmailField('Email Address',null=False,blank=False,primary_key=True)
    password = models.CharField(max_length=100,null=False,blank=False)
    document = models.FileField(upload_to='documents/')
    
    def __str__(self):
        return self.name
    
    
class organizations(models.Model):
    name = models.CharField(max_length=100,null=False,blank=False)
    email = models.EmailField('Email Address',null=False,blank=False,primary_key=True)
    password = models.CharField(max_length=100,null=False,blank=False)
    description = models.TextField(max_length = 250,null=False,blank=False)
    image1 = models.ImageField(upload_to=get_file_path,null=False,blank=False)
    image2 = models.ImageField(upload_to=get_file_path,null=False,blank=False)
    location = models.CharField(max_length=200,null=False,blank=False) 
    contact = PhoneField(null=False,blank=False, help_text='Contact phone number')
    document = models.FileField(upload_to='documents/')
        
    def __str__(self):
        return self.name