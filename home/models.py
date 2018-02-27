from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailsearch import index

from sitecore import blocks as sitecore_blocks
from sitecore.parsers import ValidateCoreBlocks

class HomePage(Page):
    body = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks]
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    api_fields = [
        'body',
    ]

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]
