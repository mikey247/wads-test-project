from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    '''
    Custom User model, where we add additional fields to user records
    '''

    bio = models.TextField(
        verbose_name='bio',
        blank=True,
    )

    team = models.CharField(
        verbose_name='team',
        max_length=255,
        blank=True,
    )

    job_title = models.CharField(
        verbose_name='job_title',
        max_length=255,
        blank=True,
    )

    country = models.CharField(
        verbose_name='country',
        max_length=255,
        blank=True,
    )

    twitter = models.CharField(
        verbose_name='twitter',
        max_length=128,
        blank=True,
    )

    receive_submission_notify_email = models.BooleanField(
        verbose_name='Receive Notifications of Submissions',
        default=False,
    )
