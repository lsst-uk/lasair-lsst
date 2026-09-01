from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
import datetime
import logging
import pytz
import sys
sys.path.append('../common')
from src import db_connect
from src import make_tag_annotator

log = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_tag_annotator(sender, instance, created, **kwargs):
    """Give every new user the tags_<username> annotator their marks live in.

    The write path provisions it lazily as well, so a failure here costs the
    user nothing and must not fail their registration.
    """
    if not created:
        return
    try:
        msl = db_connect.remote()
        make_tag_annotator.make_annotator(msl, instance.username, instance.id)
        msl.commit()
        msl.close()
    except Exception as e:
        log.error('Could not make the tags annotator for %s: %s', instance.username, e)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    recent = datetime.datetime.now() - datetime.timedelta(seconds=15)
    utc = pytz.UTC
    if not instance.last_login or instance.last_login.replace(tzinfo=utc) < recent.replace(tzinfo=utc):
        instance.profile.save()
