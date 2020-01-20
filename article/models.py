from __future__ import absolute_import, unicode_literals

import datetime

from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
 
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, ObjectList, PublishingPanel, StreamFieldPanel, TabbedInterface
from wagtail.contrib.routable_page.models import route, RoutablePageMixin
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from sitecore import blocks as sitecore_blocks
from sitecore.fields import ShortcodeRichTextField
from sitecore.models import SitePage
from sitecore.parsers import ValidateCoreBlocks

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase


import logging
logger = logging.getLogger(__name__)


class ArticleIndexPage(RoutablePageMixin, Page):
    desc = ShortcodeRichTextField(blank=True)
    per_page = models.PositiveSmallIntegerField(default=10,
                                                validators=[
                                                    MinValueValidator(1),
                                                    MaxValueValidator(100)
                                                ])

    display_title = models.BooleanField(default=True)
    display_desc = models.BooleanField(default=False)
    
    def get_context(self, request, year=None, month=None, day=None):
        # Update content to include only published posts; ordered by reverse-chronological
        context = super(ArticleIndexPage, self).get_context(request)
        all_articles = self.get_children().live().order_by('-first_published_at')

        if year:
            all_articles = all_articles.filter(first_published_at__year=year)
        if month:
            all_articles = all_articles.filter(first_published_at__month=month)
        if day:
            all_articles = all_articles.filter(first_published_at__day=day)

        paginator = Paginator(all_articles, self.per_page) 

        page = request.GET.get('page')
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles= paginator.page(paginator.num_pages)

        context['articles'] = articles
        context['year'] = year
        context['month'] = month
        context['day'] = day
        
        return context

    content_panels = Page.content_panels + [
        FieldPanel('desc', classname="full"),
        FieldPanel('per_page'),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel('display_title'),
            FieldPanel('display_desc'),
        ], heading='Page Display Options'),
    ]


    # route for sub-pages with a date specific URL for posts
    # this will NOT make a list of pages at blog/2018 just specific blogs only

    @route(r'^(?P<year>[0-9]{4})/?$')
    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/?$')
    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/?$')
    def article_index_by_year(self, request, year, month=None, day=None, name='article-index-by-date'):
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request, year=year, month=month, day=day)
        )
    
    
    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<slug>[\w-]+)/?$')
    def article_page_by_date(self, request, year, month, day, slug, name='article-by-date'):
        """Serve a single article page at URL (eg. .../2018/01/23/my-title/)"""
        article_page = get_object_or_404(
            ArticlePage,
            first_published_at__year=year,
            first_published_at__month=month,
            first_published_at__day=day,
            slug=slug
        )
        return article_page.serve(request)
            
    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<slug>[\w-]+)/(?P<sub>[/\w-]+)/?$')
    def sub_article_page_by_date(self, request, year, month, day, slug, sub, name='sub-article-by-date'):
        """Serve a single sub article page at URL (eg. .../2018/01/23/my-title/sub-article)"""
        article_page = get_object_or_404(
            ArticlePage,
            first_published_at__year=year,
            first_published_at__month=month,
            first_published_at__day=day,
            slug=slug
        )
        # sub is now of form "one/" or "one/two/" etc
        # TODO: improve for multiple children and consider query set first accessor?
        sub_article_page = article_page.get_children().live().specific().filter(slug=sub.strip("/"))
        return sub_article_page[0].serve(request)
            

    # Speficies that only BlogPage objects can live under this index page
    subpage_types = ['ArticlePage']
    

class ArticlePage(SitePage):
    """
    This model represents a default standard article for use within the Django/Wagtail sites.
    
    Classes::

    ArticlePage:
        - article image
        - intro
        - body
        + Inherits from SitePage (which adds global tag support)
    SitePage:
        - Tags
        + Inherits from Page (the default Wagtail page model)
    Page:
        - title
        - slug
        - page title (as appears in browser tab/window)
        - show in menus
        - search description (override of intro field for search if required)
        - Go live date/time
        - Expiry date/time
    """

    RENDER_TEMPLATE_CHOICES = (
        ('article_page_default.html', 'Default (Left-hand Sidebar)'),
        ('article_page_default_right.html', 'Default (Right-hand Sidebar)'),
        ('article_page_default_none.html', 'Default (No Sidebar)'),
        ('article_page_splash.html', 'Splash (Full width banner image'),
    )

    # meta panel fields

    # includes Page:title
    # includes SitePage:tags
    
    author = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Use this to override the default author/owner name (free text only).'),
        #label=_('Override author'),
    )

    article_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        #label=_('Article Banner Image'),
        help_text=_('Provide an image that spans the top of the article content (and is used as thumbnail in the blog listings unless overridden.'),
    )
    
    thumbnail_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        #label=_('Thumbnail image (override)'),
        help_text=_('Specify an alternative image for the thumbnail in blog listings if the main banner image is not suitable or a different image is desired.'),
    )
    
    # content panel fields
    
    intro = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        #label=_('Introduction and Summary'),
        help_text=_('Provide introductory content here. This will be used in the blog list pages and search result summaries.'),
    )

    body = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        #label=_('Main Body Content'),
        help_text=_('Provide the main body content here. This is not visible in the blog list and search summaries but is still searchable.'),
    )

    # settings tab panel options
    
    display_title = models.BooleanField(
        default=True,
        help_text=_('Toggle the display of the default title field.'),
    )

    render_template = models.CharField(
        # widget=forms.RadioSelect,
        # required=True,
        max_length=128,
        default='article_page_default_left.html',
        choices=RENDER_TEMPLATE_CHOICES,
    )

    splash_content = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide content for the splash area here. This will be used in the blog list pages and search result summaries.'),
    )


    # Append which fields are to be searchable
    
    search_fields = SitePage.search_fields + [
        index.SearchField('author'),
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    # Append which fields are to be accessible via the REST API

    api_fields = SitePage.search_fields + [
        'author',
        'article_image',
        'thumbnail_image',
        'intro',
        'body',
        'display_title',
        'render_template',
        'splash_content',
    ]

    # Build new meta tab panel
    
    meta_tab_panel = [
        MultiFieldPanel([
            FieldPanel('title'),
            FieldPanel('tags'),
            FieldPanel('author'),
        ], heading="Article Metadata"),
        MultiFieldPanel([
            ImageChooserPanel('article_image'),
            ImageChooserPanel('thumbnail_image'),
        ], heading="Article Banner and Thumbnail"),
    ]

    # Rebuild main content tab panel
    
    content_tab_panel = [
        MultiFieldPanel([
            StreamFieldPanel('intro')
        ], heading="Article Introduction and Summary"),
        MultiFieldPanel([
            StreamFieldPanel('body')
        ], heading="Article Main body"),
    ]

    # Rebuild promote tab panel
    
    promote_tab_panel = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('show_in_menus'),
            FieldPanel('search_description'),
        ], heading=_('Common page configuration')),
        PublishingPanel()
    ]

    # Rebuild settings tab panel - add display/override fields
    
    settings_tab_panel = [
        MultiFieldPanel([
            FieldPanel('display_title'),
        ], heading='Page Display Options'),
        MultiFieldPanel([
            FieldPanel('render_template'),
            StreamFieldPanel('splash_content'),
        ], heading='Theme and Layout Options'),
    ]

    # Rebuild edit_handler so we have all tabs
    
    edit_handler = TabbedInterface([
        ObjectList(meta_tab_panel, heading='Meta'),
        ObjectList(content_tab_panel, heading='Content'),
        ObjectList(promote_tab_panel, heading='Promote'),
        ObjectList(settings_tab_panel, heading='Settings'),
    ])


    def get_template(self, request):
        return 'article/'+self.render_template


    def set_url_path(self, parent):
        # initially set the attribute self.url_path using the normal operation
        super().set_url_path(parent=parent)

        # only modify url if page is a child of an ArticleIndexPage
        if isinstance(parent.specific,ArticleIndexPage):
            if self.first_published_at:
                self.url_path = self.url_path.replace(
                    self.slug, '{:%Y/%m/%d/}'.format(self.first_published_at) + self.slug
                )
            else:
                self.url_path = self.url_path.replace(
                    self.slug, '{:%Y/%m/%d/}'.format(timezone.now()) + self.slug
                )
