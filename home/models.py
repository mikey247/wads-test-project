from __future__ import absolute_import, unicode_literals

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from sitecore import constants
from sitecore import blocks as sitecore_blocks
from sitecore.parsers import ValidateCoreBlocks

class HomePage(Page):

    # content fields
    
    splash_image = models.ForeignKey(
        'captioned_images.CaptionImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Provide an image that spans the top of the homepage.'),
    )
    
    splash_content = StreamField(
        sitecore_blocks.SplashBlock,
        #validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide content for the splash area here.'),
    )

    intro = StreamField(
        sitecore_blocks.SplashBlock,
        #validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide introductory content here.'),
    )

    body = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide main body of content here.'),
    )

    # settings fields

    display_title = models.BooleanField(
        default=True,
        help_text=_('Toggle the display of the default title field.'),
    )

    splash_text_align = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_ALIGN_CHOICES,
        default='text-center',
        max_length=128
    )

    splash_text_colour = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        default='text-white',
        max_length=128
    )
    
    splash_bg_colour = models.CharField(
        choices=constants.BOOTSTRAP4_BACKGROUND_COLOUR_CHOICES,
        default='bg-transparent',
        max_length=128
    )

    splash_border_radius = models.IntegerField(
        default='15',
        validators=[MinValueValidator(0)]
    )

    intro_text_align = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_ALIGN_CHOICES,
        default='text-center',
        max_length=128
    )

    intro_text_colour = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        default='text-primary',
        max_length=128
    )
    
    # search and api
    
    search_fields = Page.search_fields + [
        index.SearchField('splash_content'),
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    api_fields = [
        'splash_content',
        'intro',
        'body',
    ]

    # admin panels
    # ------------
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            ImageChooserPanel('splash_image'),
            StreamFieldPanel('splash_content'),
        ], heading="Home Page Splash"),
        MultiFieldPanel([
            StreamFieldPanel('intro'),
            StreamFieldPanel('body'),
        ], heading="Home Page Content"),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel([
            FieldPanel('display_title'),
        ], heading='Page Display Options'),
        MultiFieldPanel([
            FieldPanel('splash_text_align'),
            FieldPanel('splash_text_colour'),
            FieldPanel('splash_bg_colour'),
            FieldPanel('splash_border_radius'),
        ], heading="Splash Options"),
        MultiFieldPanel([
            FieldPanel('intro_text_align'),
            FieldPanel('intro_text_colour'),
        ], heading="Intro Options"),
    ]
    
    parent_page_types = ['wagtailcore.Page']
