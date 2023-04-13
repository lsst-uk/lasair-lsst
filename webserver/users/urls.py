from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', views.register, name='register'),  # FIX ME
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name="users/login.html"), name='login'),
    path('logout/', views.logout, name='logout'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html", post_reset_login=True, success_url="/password-reset/success/"), name='password_reset_confirm'),
    path('password-reset/success/', auth_views.PasswordResetDoneView.as_view(template_name="index.html", extra_context={"alert": "You have successfully changed your password and are now logged in."}), name='password_reset_success'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name="users/password_reset.html", email_template_name="users/password_reset_email.html"), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="index.html", extra_context={"alert": "If your email is associated with a registered account, you will receive an email with instructions on how to change your password."}), name='password_reset_done'),
    path('activate/<uidb64>/<token>', views.activate, name='activate')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
