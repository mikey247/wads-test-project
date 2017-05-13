from __future__ import absolute_import, unicode_literals

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
 
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index

from sitecore import blocks as sitecore_blocks
from sitecore.fields import ShortcodeRichTextField
from sitecore.models import SitePage

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


#class ArticlePageTag(TaggedItemBase):
#    content_object = ParentalKey('article.ArticlePage', related_name='tagged_articles')


class ArticlePage(SitePage):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
#    tags = ClusterTaggableManager(through=PageTag, blank=True)
    intro = ShortcodeRichTextField(blank=True)

    body = StreamField(sitecore_blocks.CoreBlock)

    search_fields = SitePage.search_fields + [
        index.SearchField('author'),
        index.SearchField('date'),
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    api_fields = SitePage.search_fields + [
        'author',
        'date',
#        'tags',
        'intro',
        'body',
    ]

    content_panels = SitePage.content_panels + [
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('date'),
#            FieldPanel('tags'),
            FieldPanel('intro'),
        ], heading="Article Information"),
        StreamFieldPanel('body'),
    ]
