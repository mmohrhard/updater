from __future__ import unicode_literals

from django.db import models

class MarFile(models.Model):
    url = models.URLField()
    size = models.IntegerField()
    hash = models.CharField(max_length=128) # hex length of a sha512 hash
    hash_function = models.CharField(max_length=20)

class LanguageFile(models.Model):
    language = models.CharField(max_length=20)
    mar_file = models.ForeignKey(MarFile, unique=True)
    release = models.ForeignKey('Release', db_index=True)

class PartialUpdate(models.Model):
    mar_file = models.ForeignKey(MarFile, unique=True)
    old_release = models.ForeignKey('Release', related_name='patial_update_dests', db_index=True)
    new_release = models.ForeignKey('Release', related_name='partial_updates')

class PartialLanguageUpdate(models.Model):
    update = models.ForeignKey(PartialUpdate, unique=True)
    language = models.CharField(max_length=20)

class UpdateChannel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Release(models.Model):
    name = models.CharField(max_length=100)
    channel = models.ForeignKey(UpdateChannel, db_index=True)
    product = models.CharField(max_length=50, db_index=True)
    os = models.CharField(max_length=50, db_index=True)
    added = models.DateTimeField(auto_now=True, db_index=True)
    
    see_also = models.URLField(default='')

    release_file = models.ForeignKey(MarFile, unique=True)
