# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.conf import settings


class Indeedlistings(models.Model):
    listing_id = models.CharField(primary_key=True, max_length=255)
    #user_id = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='user_id', default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=256, blank=True, null=True)
    location = models.CharField(max_length=32, blank=True, null=True)
    distance = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    eta = models.IntegerField(blank=True, null=True)
    published = models.DateTimeField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=2048, blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)
    remove = models.IntegerField(blank=True, null=True)
    finish = models.IntegerField(blank=True, null=True)
    in_progress = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey('Urls', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'IndeedListings'


class Providers(models.Model):
    provider_id = models.IntegerField(primary_key=True)
    name = models.CharField(db_column='Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    url = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Providers'


class Urls(models.Model):
    category_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='user_id', default=1)
    category_name = models.CharField(max_length=100, blank=True, null=True)
    provider = models.ForeignKey(Providers, models.DO_NOTHING, db_column='provider', blank=True, null=True)
    keywords = models.CharField(max_length=1024, blank=True, null=True)
    url = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Urls'



class PhraseList(models.Model):

    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=True)
    phrases = models.CharField(max_length=4096)  # Adjust max_length as needed
    def clean(self):
        # Split the input into a list and remove any leading/trailing spaces
        self.phrases = [phrase.strip() for phrase in self.phrases.split(',') if phrase.strip()]
