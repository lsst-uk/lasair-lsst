from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
import datetime
import pytz


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    recent = datetime.datetime.now() - datetime.timedelta(seconds=15)
    utc = pytz.UTC
    if not instance.last_login or instance.last_login.replace(tzinfo=utc) < recent.replace(tzinfo=utc):
        instance.profile.save()
