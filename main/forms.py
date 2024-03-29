from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
    
class ProfileForm(forms.ModelForm):
    document1=forms.FileField(required=True)
    document2=forms.FileField(required=True)
    
    class Meta:
        model = Profile
        fields = ["role", "document1", "document2", "organisation_name", "description", "image1", "image2", "location", "contact"]

class PostForm(forms.ModelForm):
    file = forms.FileField(required=True)
    class Meta:
        model = Post
        fields = ["title", "file"]
