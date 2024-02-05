from django.db import models
from django.contrib.auth.models import User

class MmaWatchmap(Watchmap):
    """MmaWatchmap. Gravy waves etc. Inherits from Watchmap.
    """

    # ID for all the MmaWatchmaps
    mw_id = models.AutoField(primary_key=True)

    # date as reported by LigoVirgo++
    event_date   = models.DateTimeField(editable=False, blank=True, null=True)

    # the skymap of a given event gets upgrades
    version      = models.CharField(max_length=16, blank=True, null=True)

    # time at which mataches are started to be made, not date_expire below
    date_active  = models.DateTimeField(editable=False, blank=True, null=True)

    area10 = models.Float()  # sq deg in 10% of skymap
    area50 = models.Float()  # sq deg in 50% of skymap
    area90 = models.Float()  # sq deg in 90% of skymap

    # URL of FITS file
    fits         = models.CharField(max_length=256, blank=True, null=True)

    ### ##########
    # Below depends on what kind of MMA event we are handling 

    # (eg namespace is LVK, IceCube, Fermi, etc)
    # Each should cite a place to find ut what the params are
    # The otherId is their identifier. So our ident is namespace:otherId
    namespace    = models.CharField(max_length=16, blank=True, null=True)
    otherId      = models.CharField(max_length=256, blank=True, null=True)

    # finding out about this namespace, meaning of params, etc
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
