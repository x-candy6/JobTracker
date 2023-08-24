from django.db import models
from django.conf import settings

# Create your models here.

class Profile(models.Model):
    id = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='id', primary_key=True)
    distance = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    resume = models.TextField(blank=True, null=True)
    cover = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Profile'
