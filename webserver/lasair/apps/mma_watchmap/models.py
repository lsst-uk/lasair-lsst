from django.db import models
from django.contrib.auth.models import User
import sys

class MmaWatchmap(models.Model):
    """MmaWatchmap. Gravy waves etc. 
    """

    # ID for all the MmaWatchmaps
    mw_id = models.AutoField(primary_key=True)

    # date as reported by LigoVirgo++
    event_tai    = models.FloatField()
    event_date   = models.DateTimeField(editable=False, blank=True, null=True)

    moc10 = models.TextField(blank=True, null=True)
    moc50 = models.TextField(blank=True, null=True)
    moc90 = models.TextField(blank=True, null=True)
    mocimage = models.TextField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    public = models.BooleanField(blank=True, null=True)

    area10 = models.FloatField()  # sq deg in 10% of skymap
    area50 = models.FloatField()  # sq deg in 50% of skymap
    area90 = models.FloatField()  # sq deg in 90% of skymap

    # (eg namespace is LVK, IceCube, Fermi, etc)
    # Each should cite a place to find ut what the params are
    # The otherId is their identifier, and there is version. 
    # So our full ident is namespace:otherId:version
    namespace    = models.CharField(max_length=16,  blank=True, null=True)
    otherId      = models.CharField(max_length=256, blank=True, null=True)
    version      = models.CharField(max_length=256, blank=True, null=True)
    more_info    = models.CharField(max_length=1024, blank=True, null=True)
    # their parameters ....
    params       = models.JSONField()

# example
#{
#    'BBH': 0.99
#    'BNS': 0.0
#    'NSBH': 0.0
#    'Terrestrial': 0.01
#    'far': 4.521287e-09
#}

    class Meta:
        """Meta.
        """

        managed = True
        db_table = 'mma_areas'

    def __str__(self):
        return self.namespace + ':' + self.otherId +_+ + self.version
