from datetime import datetime
from website import settings
import string
from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm, ProfileForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from .models import Post, Profile
from django.http import FileResponse, HttpResponse
from digital_signatures import signatures
from django.core.files import File
import os
import pyotp
import random
from django.core.mail import send_mail
import base64

def make_secret_key(random_string):
    return str(datetime.date(datetime.now())) + random_string

def administrator(request):
    return render(request, 'main/administrator.html')

@login_required(login_url="/login")
def home(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'patient':
            return redirect("/patient")
        elif request.user.profile.role == 'healthcarepro':
            return redirect("/healthcarepro")
        elif request.user.profile.role == 'hospital':
            return redirect("/hospital")
        elif request.user.profile.role == 'pharmacy':
            return redirect("/pharmacy")
        elif request.user.profile.role == 'insurance':
            return redirect("/insurance")
        else:
            return redirect("/home")
    else:
        return redirect("/login")

@login_required(login_url="/login")
def patient(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'patient':            
            #Patients can view and search through a catalog of healthcare professionals and organizations.
            if request.method == 'POST':
                if request.POST.get('download-user'):
                    try:
                        post_id = request.POST.get('download-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.author_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")
                elif request.POST.get('download-shared-user'):
                    try:
                        post_id = request.POST.get('download-shared-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.share_to_user_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")
                elif request.POST.get('delete-user'):
                    try:
                        post_id = request.POST.get('delete-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.author == request.user:
                        post.delete()
                        return redirect("/patient")
                    else:
                        return HttpResponse("Error! You do not have permission to delete this document.")
                #if post request contains receiver
                elif request.POST.get('receiver'):
                    receiver = request.POST.get('receiver')
                    #print(int(receiver))
                    return redirect("/share/"+receiver)
                else:
                    type=request.POST.get('type')
                    search=request.POST.get('search')

                    if type == 'healthcarepro':
                        # search for healthcarepro and name as user first name and last name
                        results = Profile.objects.filter(role='healthcarepro', user__first_name__icontains=search) | Profile.objects.filter(role='healthcarepro', user__last_name__icontains=search)
                        return render(request, 'main/patient.html', {'results':results})
                    elif type == 'hospital':
                        results = Profile.objects.filter(role='hospital', organisation_name__icontains=search)
                        return render(request, 'main/patient.html', {'results': results})
                    elif type == 'pharmacy':
                        results = Profile.objects.filter(role='pharmacy', organisation_name__icontains=search)
                        return render(request, 'main/patient.html', {'results': results})
                    elif type == 'insurance':
                        results = Profile.objects.filter(role='insurance', organisation_name__icontains=search)
                        return render(request, 'main/patient.html', {'results': results})
                    else:
                        return redirect("/patient")
            else:
                user_posts=Post.objects.filter(author=request.user)
                shared_with_user_posts=Post.objects.filter(share_to_user=request.user)
                return render(request, 'main/patient.html', {'user_posts':user_posts, 'shared_with_user_posts':shared_with_user_posts})

        else:
            return redirect("/home")
    else:
        return redirect("/login")

@login_required(login_url="/login")
def insurance(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'insurance':
            if request.method == 'POST':
                if request.POST.get('download-user'):
                    try:
                        post_id = request.POST.get('download-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.author_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")
                elif request.POST.get('download-shared-user'):
                    try:
                        post_id = request.POST.get('download-shared-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.share_to_user_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")

                # Code here to search for users and share documents with them
            else:
                user_posts=Post.objects.filter(author=request.user)
                shared_with_user_posts=Post.objects.filter(share_to_user=request.user)
                shared_with_user_posts_list=[]

                for post in shared_with_user_posts:
                    #print all attributes of post as a dictionary
                    post_data=vars(post)
                    if signatures.verify_pdf(post.certificate_user.path, post.file.path):
                        post_data['is_signed']=True
                    else:
                        post_data['is_signed']=False
                    shared_with_user_posts_list.append(post_data)

                return render(request, 'main/insurance.html', {'user_posts':user_posts, 'shared_with_user_posts':shared_with_user_posts_list})

        else:
            return redirect("/home")
    else:
        return redirect("/login")

@login_required(login_url="/login")
def healthcarepro(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'healthcarepro':
            if request.method == 'POST':
                if request.POST.get('download-user'):
                    try:
                        post_id = request.POST.get('download-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.author_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")
                elif request.POST.get('download-shared-user'):
                    try:
                        post_id = request.POST.get('download-shared-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.share_to_user_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")

                # Code here to search for users and share documents with them
            else:
                user_posts=Post.objects.filter(author=request.user)
                shared_with_user_posts=Post.objects.filter(share_to_user=request.user)
                shared_with_user_posts_list=[]

                for post in shared_with_user_posts:
                    #print all attributes of post as a dictionary
                    post_data=vars(post)
                    if signatures.verify_pdf(post.certificate_user.path, post.file.path):
                        post_data['is_signed']=True
                    else:
                        post_data['is_signed']=False
                    shared_with_user_posts_list.append(post_data)

                return render(request, 'main/healthcarepro.html', {'user_posts':user_posts, 'shared_with_user_posts':shared_with_user_posts_list})

        else:
            return redirect("/home")
    else:
        return redirect("/login")

@login_required(login_url="/login")
def pharmacy(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'pharmacy':
            if request.method == 'POST':
                if request.POST.get('download-user'):
                    try:
                        post_id = request.POST.get('download-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.author_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")
                elif request.POST.get('download-shared-user'):
                    try:
                        post_id = request.POST.get('download-shared-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.share_to_user_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")

                # Code here to search for users and share documents with them
            else:
                user_posts=Post.objects.filter(author=request.user)
                shared_with_user_posts=Post.objects.filter(share_to_user=request.user)
                shared_with_user_posts_list=[]

                for post in shared_with_user_posts:
                    #print all attributes of post as a dictionary
                    post_data=vars(post)
                    if signatures.verify_pdf(post.certificate_user.path, post.file.path):
                        post_data['is_signed']=True
                    else:
                        post_data['is_signed']=False
                    shared_with_user_posts_list.append(post_data)

                return render(request, 'main/pharmacy.html', {'user_posts':user_posts, 'shared_with_user_posts':shared_with_user_posts_list})

        else:
            return redirect("/home")
    else:
        return redirect("/login")

@login_required(login_url="/login")
def hospital(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'hospital':
            if request.method == 'POST':
                if request.POST.get('download-user'):
                    try:
                        post_id = request.POST.get('download-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.author_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")
                elif request.POST.get('download-shared-user'):
                    try:
                        post_id = request.POST.get('download-shared-user')
                        post = Post.objects.get(id=int(post_id))
                    except:
                        return HttpResponse("Error! Document does not exist.")
                    if post.share_to_user_id == request.user.id:
                        return FileResponse(post.file, as_attachment=True)
                    else:
                        return HttpResponse("Error! You do not have permission to download this document.")

                # Code here to search for users and share documents with them
            else:
                user_posts=Post.objects.filter(author=request.user)
                shared_with_user_posts=Post.objects.filter(share_to_user=request.user)
                shared_with_user_posts_list=[]

                for post in shared_with_user_posts:
                    #print all attributes of post as a dictionary
                    post_data=vars(post)
                    if signatures.verify_pdf(post.certificate_user.path, post.file.path):
                        post_data['is_signed']=True
                    else:
                        post_data['is_signed']=False
                    shared_with_user_posts_list.append(post_data)

                return render(request, 'main/hospital.html', {'user_posts':user_posts, 'shared_with_user_posts':shared_with_user_posts_list})

        else:
            return redirect("/home")
    else:
        return redirect("/login")



@login_required(login_url="/login")
#@permission_required("main.add_post", login_url="/login", raise_exception=True)
def share(request, receiver):
    if request.user.is_authenticated:
        try:
            receiver_user = User.objects.get(id=receiver)
        except:
            return HttpResponse("Error! receiver does not exist.")
        if request.user.profile.role == receiver_user.profile.role:
            return HttpResponse("Error! You cannot share among the users of same role.")
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.share_to_user = receiver_user
                certificate_path, private_key_path = signatures.load(post.author.username)
                post.certificate_user = File(open(certificate_path, 'rb'))
                post.save()
                signatures.sign_pdf(post.file.path, certificate_path, private_key_path)
                # remove certificate of certificate_path
                os.remove(certificate_path)
                return redirect("/home")
            else:
                return HttpResponse("Error! Invalid form data. Make sure size of file is less than 5MB and file type is pdf.")
                
        else:
            form = PostForm()

        return render(request, 'main/share.html', {"form": form})
    else:
        return redirect("/login")


def sign_up(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.refresh_from_db()
            user.is_active = False
            user.save()
            profile = profile_form.save(commit=False)
            if profile.user_id is None:
                profile.user_id = user.id
            if profile.role == 'patient' or profile.role == 'healthcarepro':
                profile.organisation_name = None
                profile.description = None
                profile.image1 = None
                profile.image2 = None
                profile.location = None
                profile.contact = None
            else:
                if profile.organisation_name is None or profile.description is None or profile.image1 is None or profile.image2 is None or profile.location is None or profile.contact is None:
                    # error, redirect to sign up page
                    return HttpResponse("Error! Please fill in all the required fields during Sign Up based on your role.")
            profile.save()
            request.session['otp_user_id'] = user.id
            email = user.email
            secret_key = make_secret_key(''.join(random.choices(string.ascii_uppercase + string.digits, k=10))) + user.email
            print(secret_key)
            encoded_key = base64.b32encode(secret_key.encode())
            one_time_password = pyotp.TOTP(encoded_key, interval=300)  
            subject = 'Validating OTP'
            message = '\nThe 6 digit OTP is: ' + str(
                one_time_password .now()) + '\n\nThis is a system-generated response for your OTP. Please do not reply to this email.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)
            request.session['otp_key'] = secret_key
            return redirect("/otp")

            # if (login(request, user)):
            #     return redirect("/home")
            # else:
            #     return HttpResponse("Thank you for signing up. Your account is pending review by the admin and will be activated soon.")
            
        else:
            print(user_form.errors)

    else:
        user_form = RegisterForm()
        profile_form = ProfileForm()

    return render(request, 'registration/sign_up.html', {"user_form": user_form, "profile_form": profile_form})

def otp(request):
    if request.user.is_authenticated:
        return HttpResponse("<h1>Error</h1><p>Bad Requestttt</p>")

    if 'otp_user_id' not in request.session.keys():
        return HttpResponse("<h1>Error</h1><p>Bad Request</p>")

    if request.method == "GET":
        user = User.objects.get(id=request.session['otp_user_id'])
        args = {"email": user.email}
        return render(request, "registration/otp.html", args)
    
    elif request.method == "POST":
        secret_key = request.session['otp_key']
        print(secret_key)
        encoded_key = base64.b32encode(secret_key.encode())
        request.session.pop('otp_key')
        one_time_password = pyotp.TOTP(encoded_key, interval=300)
        user = User.objects.get(id=request.session['otp_user_id'])
        request.session.pop('otp_user_id')
        print(one_time_password.now())
        print(request.POST["otp"])
        if one_time_password.verify(request.POST["otp"]):
            #login(request, user)
            return HttpResponse("<h1>Success</h1><p>OTP verified successfully. Admin will review your account and activate it soon. </p> <p> Click <a href='\home'>here</a> to go to home page.</p>")
        else:
            # delete the user and profile from the database
            user_profile = Profile.objects.get(user_id=user.id)
            user_profile.delete()
            user.delete()
            return HttpResponse(f"<h1>Error</h1><p> UR TRASH OTP was wrong or has been expired </p><p><a href='{'/sign-up'}'>Try again</a></p>")
    else:
        return HttpResponse("<h1>Error</h1><p>Bad Request</p>")

@login_required(login_url="/login")
def profile_page(request):
    if request.user.is_authenticated:
        editable = False
        try:
            user = User.objects.get(id=request.user.id)
            if request.method == 'POST':
                #print(request.POST)
                if request.POST.get('editable')=='True':
                    editable = True
                    return render(request, 'main/profile.html', {"user_details": user, "editable": editable})  
                else:
                    editable = False
                    user.first_name = request.POST.get('first_name')
                    user.last_name = request.POST.get('last_name')
                    if request.user.profile.role != 'patient' and request.user.profile.role != 'healthcarepro':
                        profile = Profile.objects.get(user_id=request.user.id)
                        profile.contact = request.POST.get('contact')
                        profile.description = request.POST.get('description')
                        profile.save()
                    user.save()
                    return render(request, 'main/profile.html', {"user_details": user, "editable": editable})     
        except:
            return HttpResponse("Error! User does not exist.")
        
        return render(request, 'main/profile.html', {"user_details": user, "editable": editable})
        
