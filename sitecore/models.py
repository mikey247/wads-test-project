from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailadmin.edit_handlers import TabbedInterface, ObjectList, FieldPanel


@register_setting
class SiteSettings(BaseSetting):

    def get_context(self, request):
        context = super(SiteSettings, self).get_context(request)
        context['site_settings'] = self.for_site(request.site)
        return context

    class Meta:
        verbose_name = 'Custom Site Settings'

    # Theme settings
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

    # Social media settings
    twitter = models.URLField(blank=True, help_text='Twitter Account')

    # create the panels
    theme_tab_panel = [
        FieldPanel('bootstrap_theme'),
    ]

    social_tab_panel = [
        FieldPanel('twitter'),
    ]

    # Combine into tabbed panel interface
    edit_handler = TabbedInterface([
        ObjectList(theme_tab_panel, heading='Theme'),
        ObjectList(social_tab_panel, heading='Social Media'),
    ])
