from __future__ import absolute_import, unicode_literals

import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
 
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index

from sitecore import blocks as sitecore_blocks
from sitecore.fields import ShortcodeRichTextField
from sitecore.models import SitePage
from sitecore.parsers import ValidateCoreBlocks

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase


class ArticleIndexPage(Page):
    desc = ShortcodeRichTextField(blank=True)
    per_page = models.PositiveSmallIntegerField(default=10,
                                                validators=[
                                                    MinValueValidator(1),
                                                    MaxValueValidator(100)
                                                ])

    def get_context(self, request):
        # Update content to include only published posts; ordered by reverse-chronological
        context = super(ArticleIndexPage, self).get_context(request)
        all_articles = self.get_children().live().order_by('-first_published_at')

        paginator = Paginator(all_articles, self.per_page) 

        page = request.GET.get('page')
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles= paginator.page(paginator.num_pages)

        context['articles'] = articles

        return context

    content_panels = Page.content_panels + [
        FieldPanel('desc', classname="full"),
        FieldPanel('per_page'),
    ]


class ArticlePage(SitePage):
    author = models.CharField(max_length=255, blank=True, help_text=_('Use this to override the default author/owner name.'))
    intro = ShortcodeRichTextField(blank=True, help_text=_('Provide introductory text here to summarise the article. Content appears in blog style lists and search result summaries.'))

    body = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks]
    )

    search_fields = SitePage.search_fields + [
        index.SearchField('author'),
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    api_fields = SitePage.search_fields + [
        'author',
        'intro',
        'body',
    ]

    content_panels = SitePage.content_panels + [
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('intro'),
        ], heading="Article Overview"),
        MultiFieldPanel([
            StreamFieldPanel('body')
        ], heading="Main body (Streamfield)"),
    ]
