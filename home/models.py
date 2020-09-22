from __future__ import absolute_import, unicode_literals

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, PrivacyModalPanel, PublishingPanel, StreamFieldPanel, TabbedInterface
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
    #   title - inherited
    
    intro = StreamField(
        sitecore_blocks.SplashBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide introductory content here.'),
    )

    body = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide main body of content here.'),
    )

    # meta fields
    #   tags - inherited
    #   search_desc inherited

    # promote fields
    #   slug - inherited
    #   page_title - inherited
    #   show_in_menus = inherited
    
    # splash fields
    
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
    
    # settings fields

    display_title = models.BooleanField(
        default=True,
        help_text=_('Toggle the display of the default title field.'),
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
    
    # Rebuild main content tab panel

    content_tab_panel = [
        FieldPanel('title'),
        StreamFieldPanel('intro'),
        StreamFieldPanel('body'),
    ]

    # Build new meta tab panel
    
    meta_tab_panel = [
        FieldPanel('search_description'),
    ]

    # Build new splash tab panel
    
    splash_tab_panel = [
        ImageChooserPanel('splash_image'),
        StreamFieldPanel('splash_content'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('splash_text_align'),
                FieldPanel('splash_text_colour'),
            ]),
            FieldRowPanel([
                FieldPanel('splash_bg_colour'),
                FieldPanel('splash_border_radius'),
            ]),
        ], heading=_('Splash Settings')),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('intro_text_align'),
                FieldPanel('intro_text_colour'),
            ]),
        ], heading=_('Inset Settings')),
    ]

    # Rebuild settings tab panel - add display/override fields
    
    settings_tab_panel = [
        FieldPanel('display_title'),
    ]

    # Rebuild promote tab panel
    
    promote_tab_panel = [
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('show_in_menus'),
    ]

    # Build new publish tab panel

    publish_tab_panel = [
        PublishingPanel(),
        PrivacyModalPanel(),
    ]
    
    
    # Rebuild edit_handler so we have all tabs
    
    edit_handler = TabbedInterface([
        ObjectList(content_tab_panel, heading='Content'),
        ObjectList(meta_tab_panel, heading='Meta'),
        ObjectList(promote_tab_panel, heading='Promote'),
        ObjectList(settings_tab_panel, heading='Settings'),
        ObjectList(splash_tab_panel, heading='Splash'),
        ObjectList(publish_tab_panel, heading='Publish'),
    ])

    
    
    parent_page_types = ['wagtailcore.Page']
