from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase

class ArticleIndexPage(Page):
    intro = RichTextField(blank=True)

    def get_context(self, request):
        # Update content to include only published posts; ordered by reverse-chronological
        context = super(ArticleIndexPage, self).get_context(request)
        articles = self.get_children().live().order_by('-first_published_at')
        context['articles'] = articles
        return context

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
    ]


class ArticlePageTag(TaggedItemBase):
    content_object = ParentalKey('ArticlePage', related_name='tagged_items')


class ArticlePage(Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
    tags = ClusterTaggableManager(through=ArticlePageTag, blank=True)

    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        #('image', blocks.ImageChooserBlock()),
        #('', blocks.Block()),
    ])

    search_fields = Page.search_fields + [
        index.SearchField('author'),
        index.SearchField('body'),
    ]

    api_fields = [
        'date',
        'body',
        'tags'
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('date'),
            FieldPanel('tags'),
        ], heading="Blog Information"),
        StreamFieldPanel('body'),
    ]
