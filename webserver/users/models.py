from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.conf import settings
import os
from lasair.utils import bytes2string
import io
from django.core.validators import FileExtensionValidator


class Profile(models.Model):

    if settings.DEBUG:
        staticRoot = settings.STATICFILES_DIRS[0]
    else:
        staticRoot = settings.STATIC_ROOT

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', validators=[FileExtensionValidator(allowed_extensions=['gif', 'jpeg', 'jpg', 'png'])])

    with open(staticRoot + '/img/default.jpg', mode='rb') as readFile:
        defaultImage = readFile.read()
        defaultImage = bytes2string(defaultImage)
        image_b64 = models.TextField(blank=True, null=True, default=defaultImage)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format=img.format)
        self.image_b64 = bytes2string(imgByteArr.getvalue())
