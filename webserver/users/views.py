import random
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
#from rest_framework.authtoken.models import Token
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
import sys
#from .utils import account_activation_token
from django.template.loader import render_to_string
#from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
#from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

def password_reset(request):
    if request.method != "POST":
        return render(request, 'users/password_reset.html')
    else:
        if not 'input_code' in request.POST:
            code = '%06d' % random.randrange(999999)
            email_address = request.POST.get("email")
            User = get_user_model()
            try:
                users = User.objects.filter(email=email_address)
                user = users[0]
            except:
                message.error('Email address not registered')

            mail_subject = "Activate your Lasair account."
            message = render_to_string("users/password_reset_email.html", 
                      { 'username': user.username, 'code': code, })
            email = EmailMessage(mail_subject, message, to=[email_address])
            if not email.send():
                messages.error(request, 
                f'Problem sending email to {email_address}, please check you typed it correctly.')
            hashcode = str(hash(code))
            return render(request, 'users/password_reset_confirm.html', 
                  {'email': email_address, 'hashcode':hashcode})
        else:
            input_code   = request.POST.get("input_code")
            hashcode     = request.POST.get("hashcode")
            email_address = request.POST.get("email")
            new_password = request.POST.get("new_password1")
            User = get_user_model()
            try:
                users = User.objects.filter(email=email_address)
                user = users[0]
            except:
                messages.error(request, "User not found")

            if str(hash(input_code)) == hashcode:
                user.set_password(new_password)
                messages.success(request, "Your password is changed. Now you can login to your account.")
                return redirect('login')
            else:
                messages.error(request, "Activation code doesn't match.")
                return render(request, 'users/password_reset_confirm.html',
                  {'email': email_address, 'hashcode':hashcode})

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            code = '%06d' % random.randrange(999999)
            email_address = form.cleaned_data.get('email')
            mail_subject = "Activate your Lasair account."
            message = render_to_string("users/email_verification_email.html", 
               { 'code': code, })
            email = EmailMessage(mail_subject, message, to=[email_address])
            if not email.send():
                messages.error(request, 
                f'Problem sending email to {email_address}, please check you typed it correctly.')

            hashcode = str(hash(code))
            return render(request, 'users/activation_code.html', 
                          {'email': email_address, 'hashcode':hashcode})
        else:
            messages.error(request, "Form is not valid")
    else:
        form = UserRegisterForm()
        return render(request, 'users/register.html', {'form': form})


def activate(request):
    hashcode   = request.POST.get("hashcode")
    input_code = request.POST.get("input_code")
    email      = request.POST.get("email")

    User = get_user_model()
    try:
        users = User.objects.filter(email=email)
        user = users[0]
    except:
        user = None

    if user is not None and str(hash(input_code)) == hashcode:
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for verifying the activation code. Now you can login to your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation code is invalid!")

    return redirect('index')

@login_required
def profile(request):

    token, created = Token.objects.get_or_create(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            p_form.save()
            u_form.save()
            messages.success(request, f'Your account has been updated.')
            return redirect('profile')
    else:
        # GET REQUEST
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'token': token.key
    }
    return render(request, "users/profile.html", context)


@login_required(redirect_field_name=None)
def logout(request):
    # message user or whatever
    template_name = "users/logout.html"
    context = {
        'username': request.user.username,
        'profile_image': request.user.profile.image_b64
    }
    auth_logout(request)
    return render(request, "users/logout.html", context)
    # return logout(request)
