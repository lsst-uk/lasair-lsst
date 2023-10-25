from django.db import models
# A WATCHLIST IS OWNED BY A USER AND GIVEN A NAME AND DESCRIPTION
# ONLY ACTIVE WATCHLISTS ARE RUN AGAINST THE REALTIME INGESTION
# THE PREQUEL_WHERE CAN BE USED TO SELECT WHICH CANDIDATES ARE COMPARED WITH THE WATCHLIST
from django.contrib.auth.models import User


class WatchlistCone(models.Model):
    """WatchlistCone.
    """

    cone_id = models.AutoField(primary_key=True)
    wl = models.ForeignKey('Watchlist', models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)
    ra = models.FloatField(blank=True, null=True)
    decl = models.FloatField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)

    class Meta:
        """Meta.
        """
        managed = True
        db_table = 'watchlist_cones'


class Watchlist(models.Model):
    """Watchlist.
    """

    wl_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, db_column='user', blank=True, null=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(max_length=4096, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    public = models.BooleanField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)
    date_created  = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=    True, editable=False, blank=True, null=True)
    date_expire   = models.DateTimeField(                   editable=True,  blank=True, null=True)

    class Meta:
        """Meta.
        """
        managed = True
        db_table = 'watchlists'

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ': ' + self.name
