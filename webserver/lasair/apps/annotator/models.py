from django.db import models
from django.contrib.auth.models import User

# ANNOTATORS BELONG TO A USER


class Annotators(models.Model):
    topic = models.CharField(primary_key=True, max_length=32)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING, db_column='user', blank=True, null=True)
    username = models.CharField(max_length=32, blank=True, null=True)
    password = models.CharField(max_length=32, blank=True, null=True)
    url = models.CharField(max_length=1024, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    public = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'annotators'

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ': ' + self.topic
