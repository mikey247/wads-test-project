"""
Sitecore models package for implementing site settings
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django.db import models

from wagtail.admin.panels import FieldPanel, ObjectList, MultiFieldPanel, TabbedInterface
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.models import Site

from sitecore import constants

# from siteconfig.settings.local import DEFAULT_FROM_EMAIL


@register_setting(icon = 'mail')
class EmailSettings(BaseSetting):

        def get_context(self, request):
            context = super().get_context(request)
            context['site'] = Site.find_for_request(request)
            return context

        class Meta:
            verbose_name = 'Email Settings'

        from_email = models.CharField(
            # default=DEFAULT_FROM_EMAIL,
            help_text='The email you want to use to send the emails. Leave as default if you haven\'t set-up a shared mailbox',
            max_length=512
        )

        # Approved Email

        approval_email_subject = models.CharField(
            max_length = 256,
            blank=True,
            verbose_name='Approval Email - Subject Header',
            help_text='Subject header to send an email.'
        )

        approval_email_content = models.TextField(
            blank=True,
            verbose_name= 'Approval Email - Content',
            help_text='Email content to send to users.'
        )
        

@register_setting
class SiteSettings(BaseSetting):
    """
    This registers new site settings options (per site) in the Wagtail admin panels.
    Limited functionality is provided here to set the (Bootstrap 4) theme.
    Settings can be grouped and provided with tabbed panels for display.
    """
    def get_context(self, request):
        context = super().get_context(request)
        context['site'] = Site.find_for_request(request)
        return context

    
    class Meta:
        verbose_name = 'Customization'


    bootstrap_theme = models.CharField(
        max_length = 32,
        choices=sorted(constants.BOOTSTRAP5_THEME_CHOICES),
        help_text='Select a Bootstrap Theme for the site',
        default=constants.INITIAL_BOOTSTRAP5_THEME
    )

    code_theme = models.CharField(
        max_length = 32,
        choices=sorted(constants.WAGTAIL_CODE_BLOCK_THEME_CHOICES),
        help_text='Select a Code Theme for code blocks',
        default= constants.INITIAL_WAGTAIL_CODE_BLOCK_THEME,
    )

    brand_logo = models.ForeignKey(
        'sitecore.SiteImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Provide an image for the navigation bar logo (preferably small).',
    )
    
    brand_icon = models.CharField(
        max_length=64,
        default='fa fa-home',
        blank=True,
        help_text='Provide the name of a Font Awesome icon (as an alternative to a logo image) to be used as the logo in the main navigation bar.',
    )

    brand_name = models.CharField(
        max_length=64,
        blank=True,
        help_text='Provide some text for the brand name next to the logo in the main navigation bar.',
    )

    brand_link = models.URLField(
        blank=True,
        help_text='Provide the URL you wish the logo to link to.',
    )

    navbar_expand = models.CharField(
        max_length = 2,
        choices=constants.NAVBAR_RESPONSIVE_SIZE_CHOICES,
        help_text='Select the media size at which the navbar menu collapses',
        default='lg',
    )

    navbar_text_colour_mode = models.CharField(
        max_length = 16,
        choices=constants.NAVBAR_TEXT_COLOUR_MODE,
        help_text='Select the text foreground colour mode of the navigation bar',
        default='navbar-dark',
    )
    
    navbar_background_colour = models.CharField(
        max_length = 32,
        choices=constants.BOOTSTRAP5_BACKGROUND_COLOUR_CHOICES,
        help_text='Select the background colour of the navigation bar',
        default='bg-primary',
    )
    
    navbar_outer_class = models.CharField(
        max_length = 32,
        choices=constants.NAVBAR_OUTER_CLASS,
        help_text='Select the class of the div that encloses the navbar (container for now; none for full width)',
        default=constants.NAVBAR_OUTER_CLASS_DEFAULT,
        blank=True,
    )
    
    # Social media settings
    twitter = models.CharField(
        max_length = 128,
        blank=True,
        help_text='Twitter Account'
    )

    social_share = models.BooleanField(
        default=True,
        help_text='Select if you want social share button at the bottom of articles and events'
    )

    # Analytics settings
    ga_tracking_id = models.CharField(
        max_length = 32,
        blank=True,
        help_text='Google Analytics Tracking ID (UA-#########-#)'
    )

    meta_description = models.CharField(
        max_length = 1024,
        blank=True,
        help_text='Page head meta-description field for SEO. Not visible but machine readable.'
    )

    meta_keywords = models.CharField(
        max_length = 1024,
        blank=True,
        help_text='Page head meta-keywords field for SEO. Comma separated list of terms. Not visible but machine readable.'
    )

    meta_author = models.CharField(
        max_length = 1024,
        blank=True,
        help_text='Page head meta-author field for SEO. Comma separated list of names and organisations. Not visible but machine readable.'
    )

    # create the panels

    branding_tab_panel = [
        FieldPanel('brand_logo'),
        FieldPanel('brand_icon'),
        FieldPanel('brand_name'),
        FieldPanel('brand_link'),
    ]

    navigation_tab_panel = [
        FieldPanel('navbar_expand'),
        FieldPanel('navbar_text_colour_mode'),
        FieldPanel('navbar_background_colour'),
        FieldPanel('navbar_outer_class'),
    ]
 
    theme_tab_panel = [
        FieldPanel('bootstrap_theme'),
        FieldPanel('code_theme'),
    ]

    analytics_tab_panel = [
        FieldPanel('ga_tracking_id'),
        FieldPanel('meta_description'),
        FieldPanel('meta_keywords'),
        FieldPanel('meta_author'),
    ]

    social_tab_panel = [
        FieldPanel('twitter'),
        MultiFieldPanel([
            FieldPanel('social_share')
        ], heading=('Social Share')),
    ]

    # Combine into tabbed panel interface
    edit_handler = TabbedInterface([
        ObjectList(branding_tab_panel, heading='Branding'),
        ObjectList(navigation_tab_panel, heading='Navigation'),
        ObjectList(theme_tab_panel, heading='Theme'),
        ObjectList(analytics_tab_panel, heading='Analytics'),
        ObjectList(social_tab_panel, heading='Social Media'),
    ])


