from django.db import models
from django.contrib.auth.models import User


class filter_query(models.Model):
    """The filter/query model. Filters are owned by a 'User'
    """

    mq_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, db_column='user', blank=True, null=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.CharField(max_length=4096, blank=True, null=True)
    selected = models.CharField(max_length=4096, blank=True, null=True)
    conditions = models.CharField(max_length=4096, blank=True, null=True)
    tables = models.CharField(max_length=4096, blank=True, null=True)
    public = models.BooleanField(blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    topic_name = models.CharField(max_length=256, blank=True, null=True)
    real_sql = models.CharField(max_length=4096, blank=True, null=True)
    date_created = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = True
        db_table = 'myqueries'

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ': ' + self.name
