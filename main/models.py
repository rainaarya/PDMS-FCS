from tkinter import N
from django.db import models
from django.contrib.auth.models import User
from yaml import DocumentStartEvent


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='userdocuments/', null=True, blank=True)
    #user whom the author wants to share the file with
    share_to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='share_to_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, using=None, keep_parents=False):
    # to delete the physical file from the storage when the object is deleted
        storage = self.file.storage

        if storage.exists(self.file.name):
            storage.delete(self.file.name)

        super().delete()

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