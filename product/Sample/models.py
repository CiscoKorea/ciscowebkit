from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Info(models.Model):
    author = models.CharField(max_length=150)
    title = models.TextField()
    
class InfoData(models.Model):
    info_id = models.CharField(max_length=150)
    data = models.TextField()
    timestamp = models.DateTimeField()
    