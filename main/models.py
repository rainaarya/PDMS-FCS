from django.db import models
from django.contrib.auth.models import User


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
    role = models.CharField(max_length=13, choices=ROLE_CHOICES, default='default')

    def __str__(self):
        return self.role