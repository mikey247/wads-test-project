from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting
class SiteSettings(BaseSetting):
    class Meta:
        verbose_name = 'Custom Site Settings'

    DEFAULT = 'default'
    PAPER = 'paper'
    THEME_CHOICES = (
        (DEFAULT, 'Default Bootstrap 3'),
        (PAPER, 'Bootswatch: Paper'),
    )
    bootstrap_theme = models.CharField(
        max_length = 10,
        choices=THEME_CHOICES,
        help_text='Select Bootstrap 3 Theme',
        default=PAPER
    )
    
    twitter = models.URLField(help_text='Twitter Account')


