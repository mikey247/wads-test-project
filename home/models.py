from __future__ import absolute_import, unicode_literals

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, PublishingPanel, TabbedInterface
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.search import index

from sitecore import constants
from sitecore import blocks as sitecore_blocks
from sitecore.models import SitePage


class HomePage(SitePage):

    # content fields
    #   title - inherited
    
    intro = StreamField(
        sitecore_blocks.SplashBlock,
        blank=True,
        help_text=_('Provide introductory content here.'),
        use_json_field=True,
    )

    body = StreamField(
        sitecore_blocks.CoreBlock,
        blank=True,
        help_text=_('Provide main body of content here.'),
        use_json_field=True,
    )

    # meta fields
    #   tags - inherited
    #   search_description inherited

    # promote fields
    #   slug - inherited
    #   page_title - inherited
    #   show_in_menus = inherited
    
    # splash fields
    
    splash_image = models.ForeignKey(
        'sitecore.SiteImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Provide an image that spans the top of the homepage.'),
    )
    
    splash_content = StreamField(
        sitecore_blocks.SplashBlock,
        blank=True,
        help_text=_('Provide content for the splash area here.'),
        use_json_field=True
    )

    splash_text_align = models.CharField(
        choices=constants.BOOTSTRAP5_TEXT_ALIGN_CHOICES,
        default='text-center',
        max_length=128
    )

    splash_text_colour = models.CharField(
        choices=constants.BOOTSTRAP5_TEXT_COLOUR_CHOICES,
        default='text-white',
        max_length=128
    )
    
    splash_bg_colour = models.CharField(
        choices=constants.BOOTSTRAP5_BACKGROUND_COLOUR_CHOICES,
        default='bg-transparent',
        max_length=128
    )

    splash_border_radius = models.IntegerField(
        default='15',
        validators=[MinValueValidator(0)]
    )

    splash_height = models.IntegerField(
        default='50',
        validators=[MinValueValidator(10)]
    )
    
    # inset fields
    
    inset_content = StreamField(
        sitecore_blocks.SplashBlock,
        blank=True,
        help_text=_('Provide content for the inset area here.'),
        use_json_field=True
    )

    inset_text_align = models.CharField(
        choices=constants.BOOTSTRAP5_TEXT_ALIGN_CHOICES,
        default='text-center',
        max_length=128
    )

    inset_text_colour = models.CharField(
        choices=constants.BOOTSTRAP5_TEXT_COLOUR_CHOICES,
        default='text-primary',
        max_length=128
    )

    inset_bg_colour = models.CharField(
        choices=constants.BOOTSTRAP5_BACKGROUND_COLOUR_CHOICES,
        default='bg-transparent',
        verbose_name='Inset background colour',
        max_length=128
    )

    inset_border_radius = models.IntegerField(
        default='15',
        validators=[MinValueValidator(0)]
    )

    inset_style = models.CharField(
        choices=constants.INSET_STYLE_CLASS_CHOICES,
        default='container inset inset-raised',
        max_length=256
    )

    # settings fields

    display_title = models.BooleanField(
        default=True,
        help_text=_('Toggle the display of the default title field.'),
    )
    display_intro = models.BooleanField(
        default=True,
        help_text=_('Toggle the display of the page intro section.'),
    )

    # search and api
    
    search_fields = Page.search_fields + [
        index.SearchField('splash_content'),
        index.SearchField('inset_content'),
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    api_fields = [
        'intro',
        'body',
        'search_description',
        'splash_image',
        'splash_content',
        'splash_text_align',
        'splash_text_colour',
        'splash_bg_colour',
        'splash_border_radius',
        'splash_height',
        'inset_content',
        'inset_text_align',
        'inset_text_colour',
        'inset_bg_colour',
        'inset_border_radius',
        'show_in_menus',
        'display_title',
    ]

    # admin panels
    # ------------
    
    # Rebuild main content tab panel

    content_tab_panel = [
        FieldPanel('title'),
        FieldPanel('intro'),
        FieldPanel('body'),
    ]

    # Build new meta tab panel
    
    meta_tab_panel = [
        FieldPanel('search_description'),
    ]

    # Build new splash and inset tab panel
    
    splash_tab_panel = [
        FieldPanel('splash_image'),
        FieldPanel('splash_content'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('splash_text_align'),
                FieldPanel('splash_text_colour'),
            ]),
            FieldRowPanel([
                FieldPanel('splash_bg_colour'),
                FieldPanel('splash_border_radius'),
            ]),
            FieldRowPanel([
                FieldPanel('splash_height'),
            ]),
        ], heading=_('Splash Settings')),
    ]

    inset_tab_panel = [
        FieldPanel('inset_content'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('inset_style')
            ]),
            FieldRowPanel([
                FieldPanel('inset_text_align'),
                FieldPanel('inset_text_colour'),
            ]),
            FieldRowPanel([
                FieldPanel('inset_bg_colour'),
                FieldPanel('inset_border_radius'),
            ]),
        ], heading=_('Inset Settings')),
    ]

    # Rebuild promote tab panel
    
    promote_tab_panel = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
            FieldPanel('display_title'),
            FieldPanel('display_intro'),
        ], heading=_('Options')),
    ]

    # Build new publish tab panel

    publish_tab_panel = [
        PublishingPanel(),
    ]
    
    # Rebuild edit_handler so we have all tabs
    
    edit_handler = TabbedInterface([
        ObjectList(content_tab_panel, heading='Content'),
        ObjectList(splash_tab_panel, heading='Splash Image'),
        ObjectList(inset_tab_panel, heading='Inset'),
        ObjectList(promote_tab_panel, heading='Promote'),
        ObjectList(meta_tab_panel, heading='Meta'),
        ObjectList(publish_tab_panel, heading='Publish'),
    ])

    # restrict HomePage model to being a HomePage ONLY
    
    parent_page_types = ['wagtailcore.Page']
