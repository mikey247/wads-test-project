from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    bio = models.TextField(verbose_name='bio')
    team = models.CharField(verbose_name='team', max_length=255)
    job_title = models.CharField(verbose_name='job_title', max_length=255)
    country = models.CharField(verbose_name='country', max_length=255)
    twitter = models.CharField(verbose_name='twitter', max_length=128)
    receive_submission_notify_email = models.BooleanField(verbose_name='Receive Notifications of Submissions', default=False)
