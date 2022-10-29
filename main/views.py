from turtle import right
from django.shortcuts import render, redirect
from matplotlib.pyplot import get
from .forms import RegisterForm, PostForm, ProfileForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from .models import Post


@login_required(login_url="/login")
def home(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'patient':
            return render(request, 'main/patient.html')
        elif request.user.profile.role == 'healthcarepro':
            return render(request, 'main/healthcarepro.html')
        elif request.user.profile.role == 'hospital':
            return render(request, 'main/hospital.html')
        elif request.user.profile.role == 'pharmacy':
            return render(request, 'main/pharmacy.html')
        elif request.user.profile.role == 'insurance':
            return render(request, 'main/insurance.html')
        else:
            return redirect("/home")
    else:
        return redirect("/login")




@login_required(login_url="/login")
@permission_required("main.add_post", login_url="/login", raise_exception=True)
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("/home")
    else:
        form = PostForm()

    return render(request, 'main/create_post.html', {"form": form})


def sign_up(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            if profile.user_id is None:
                profile.user_id = user.id
            if profile.role == 'patient':
                profile.organisation_name = None
                profile.description = None
                profile.image1 = None
                profile.image2 = None
                profile.location = None
                profile.contact = None
            else:
                if profile.organisation_name is None or profile.document1 is None or profile.document2 is None or profile.description is None or profile.image1 is None or profile.image2 is None or profile.location is None or profile.contact is None:
                    # error, redirect to sign up page
                    return redirect("/sign-up")
            profile.save()
            login(request, user)
            return redirect("/home")
        else:
            print(user_form.errors)

    else:
        user_form = RegisterForm()
        profile_form = ProfileForm()

    return render(request, 'registration/sign_up.html', {"user_form": user_form, "profile_form": profile_form})
