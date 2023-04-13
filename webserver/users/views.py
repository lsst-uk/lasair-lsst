from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from rest_framework.authtoken.models import Token
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
import sys
from .utils import account_activation_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for verifying your email. Now you can login to your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('index')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your Lasair account."
    message = render_to_string("users/email_verification_email.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'We have sent you an email to {to_email}. Please follow the instructions to acivate your Lasair account. Can\'t find the email? Please check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, please check you typed it correctly.')


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
