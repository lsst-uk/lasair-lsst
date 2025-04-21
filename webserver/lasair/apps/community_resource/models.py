from django.db import models
from django.contrib.auth.models import User

# CommunityResource BELONG TO A USER

resourceTypes = (
    ('filter', 'filter'),
    ('watchlist', 'watchlist'),
    ('watchmap', 'watchmap'),
    ('annotator', 'annotator')
)


class community_resource(models.Model):
    resource_name = models.CharField(primary_key=True, max_length=32)
    resource_id = models.IntegerField()  # id of filter, watchlist, watchmap, annotator
    resource_type = models.CharField(max_length=10, choices=resourceTypes, default='filter')
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'community_resources'

    def __str__(self):
        return self.resource_name
