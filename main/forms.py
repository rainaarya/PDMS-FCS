from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role"]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description"]
