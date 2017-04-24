from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    country = models.CharField(verbose_name='country', max_length=255)
    twitter = models.CharField(verbose_name='twitter', max_length=128)
    
