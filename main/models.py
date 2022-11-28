from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='user-documents/', null=True, blank=True)
    certificate_user = models.FileField(upload_to='user-certificates/', null=True, blank=True)
    #user whom the author wants to share the file with
    share_to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='share_to_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blockchain_index = models.IntegerField(default=0)

    def clean(self):
        # method to check if the file is a pdf and not more than 5MB
        if self.file:
            if not self.file.name.endswith('.pdf'):
                raise ValidationError('File is not PDF Format')
            if self.file.size > 5242880:
                raise ValidationError('File is too large (> 5 MB)')
        else:
            raise ValidationError('File is missing')

    def delete(self, using=None, keep_parents=False):
        # to delete the physical file from the storage when the object is deleted
        storage = self.file.storage

        if storage.exists(self.file.name):
            storage.delete(self.file.name)
        if storage.exists(self.certificate_user.name):
            storage.delete(self.certificate_user.name)

        super().delete()

    def __str__(self):
        return self.title + "\n" + self.author.username + "\n" + self.share_to_user.username

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
    
    def clean(self):
        # method to check if the file is a pdf and not more than 5MB
        if self.document1:
            if not self.document1.name.endswith('.pdf'):
                raise ValidationError('File is not PDF Format')
            if self.document1.size > 5242880:
                raise ValidationError('File is too large (> 5 MB)')
        else:
            raise ValidationError('File is missing')

        if self.document2:
            if not self.document2.name.endswith('.pdf'):
                raise ValidationError('File is not PDF Format')
            if self.document2.size > 5242880:
                raise ValidationError('File is too large (> 5 MB)')
        else:
            raise ValidationError('File is missing')

        if self.image1:
            if not (self.image1.name.endswith('.jpg') or self.image1.name.endswith('.jpeg') or self.image1.name.endswith('.png')):
                raise ValidationError('File is not Image Format (jpg/jpeg/png)')
            if self.image1.size > 5242880:
                raise ValidationError('File is too large (> 5 MB)')

        if self.image2:
            if not (self.image2.name.endswith('.jpg') or self.image2.name.endswith('.jpeg') or self.image2.name.endswith('.png')):
                raise ValidationError('File is not Image Format (jpg/jpeg/png)')
            if self.image2.size > 5242880:
                raise ValidationError('File is too large (> 5 MB)')

    def delete(self, using=None, keep_parents=False):
        # to delete the physical file from the storage when the object is deleted
        #print("\n\ndeleting\n\n")
        storage = self.document1.storage

        #check if fields exist        
        if self.document1:
            if storage.exists(self.document1.name):
                storage.delete(self.document1.name)
        
        if self.document2:
            if storage.exists(self.document2.name):
                storage.delete(self.document2.name)
        
        if self.image1:
            if storage.exists(self.image1.name):
                storage.delete(self.image1.name)
        
        if self.image2:
            if storage.exists(self.image2.name):
                storage.delete(self.image2.name)

        super().delete()
    
    def __str__(self):
        return self.role