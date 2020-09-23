from __future__ import absolute_import, unicode_literals

import datetime

from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
 
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, ObjectList, PrivacyModalPanel, PublishingPanel, StreamFieldPanel, TabbedInterface
from wagtail.contrib.routable_page.models import route, RoutablePageMixin
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from sitecore import blocks as sitecore_blocks
from sitecore import constants
from sitecore.fields import ShortcodeRichTextField
from sitecore.models import SitePage
from sitecore.parsers import ValidateCoreBlocks

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase


import logging
logger = logging.getLogger(__name__)


class ArticleIndexPage(RoutablePageMixin, Page):
    """
    This model represents Article Index Page, for use within the Django/Wagtail sites.
    The index page will list any child pages in a "blog" style list, using content from the child page.
    e.g., thumbnail_image (or thumbnail of article_image) from the ArticlePage model
          the title, published/revised dates, author and intro fields

    By default the index is presented in reverse first_published_at date order i.e., newest first.

    The ArticleIndexPage only considers all immediate child pages and no further descendants.

    The ArticleIndexByDatePage class below extends th functionality of this class by forcing all child page
    urls to conform to a yyyy/mm/dd/slug format. 
    
    """
    
    SIDEBAR_PLACEMENT_DEFAULT='left'
    SIDEBAR_PLACEMENT_CHOICES = (
        ('left', 'Single sidebar (To left of main content'),
        ('right', 'Single sidebar (To right of main content'),
        ('none', 'No sidebars'),
    )
    
    intro = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide introductory content here. This will be used in the blog list pages and search result summaries.'),
    )

    per_page = models.PositiveSmallIntegerField(default=10,
                                                validators=[
                                                    MinValueValidator(1),
                                                    MaxValueValidator(100)
                                                ])

    display_title = models.BooleanField(default=True)
    display_intro = models.BooleanField(default=False)
    
    sidebar_placement = models.CharField(
        max_length=128,
        default='left',
        choices=SIDEBAR_PLACEMENT_CHOICES,
    )
    
    def get_context(self, request):
        # Update content to include only published posts; ordered by reverse-chronological
        context = super(ArticleIndexPage, self).get_context(request)
        all_articles = self.get_children().live().order_by('-first_published_at')

        # get the paginator obj and the current page number
        paginator = Paginator(all_articles, self.per_page) 
        page = request.GET.get('page')
        index = int(page)-1 if page is not None else 0
        
        # get list of articles for the desired page
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)

        # limit page_range of the paginator (hard-coded to 3 pages both ways)
        max_index = len(paginator.page_range)
        start_index = max(0, index - 3)
        end_index = min(max_index, start_index + 7)

        # build new page range from calculated range but also include first/last pages if not in range
        context['page_range'] = []
        if start_index > 0:
            context['page_range'].append(1)
        context['page_range'] = context['page_range'] + list(paginator.page_range)[start_index:end_index]
        if end_index < max_index:
            context['page_range'].append(max_index)
            
        context['articles'] = articles
        
        return context


    # Build new meta tab panel
    
    # Rebuild main content tab panel
    
    content_tab_panel = [
        MultiFieldPanel([
            FieldPanel('title'),
            StreamFieldPanel('intro')
        ], heading="Article Introduction and Summary"),
    ]

    # Rebuild promote tab panel
    
    promote_tab_panel = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('show_in_menus'),
            FieldPanel('search_description'),
        ], heading=_('Common page configuration')),
        PublishingPanel(),
        PrivacyModalPanel(),
    ]


    settings_tab_panel = [
        MultiFieldPanel([
            FieldPanel('per_page'),
        ], heading='Article Index Options'),
        MultiFieldPanel([
            FieldPanel('display_title'),
            FieldPanel('display_intro'),
        ], heading='Page Display Options'),
        MultiFieldPanel([
            FieldRowPanel([
#                FieldPanel('render_template'),
                FieldPanel('sidebar_placement'),
            ]),
        ], heading='Theme and Layout Options'),
#        MultiFieldPanel([
#            FieldRowPanel([
#                FieldPanel('splash_text_align'),
#                FieldPanel('splash_text_colour'),
#            ]),
#            FieldRowPanel([
#                FieldPanel('splash_bg_colour'),
#                FieldPanel('splash_border_radius'),
#            ]),
#            StreamFieldPanel('splash_content'),
#        ], heading='Splash Content and Options'),
    ]

    # Rebuild edit_handler so we have all tabs
    
    edit_handler = TabbedInterface([
#        ObjectList(meta_tab_panel, heading='Meta'),
        ObjectList(content_tab_panel, heading='Content'),
        ObjectList(promote_tab_panel, heading='Promote'),
        ObjectList(settings_tab_panel, heading='Settings'),
    ])

    def get_template(self, request):
        return f'article/article_index_page_{self.sidebar_placement}.html'



    

class ArticleIndexByDatePage(ArticleIndexPage):
    """
    This model represents Article Index By Date Page, and extends the ArticleIndexPage class above,
    for use within the Django/Wagtail sites.

    The index page will list any child pages in a "blog" style list, using content from the child page.
    e.g., thumbnail_image (or thumbnail of article_image) from the ArticlePage model
          the title, published/revised dates, author and intro fields

    By default the index is presented in reverse first_published_at date order i.e., newest first.

    The ArticleIndexPage only considers all immediate child pages and no further descendants.

    This ArticleIndexByDatePage class below extends the functionality of the parent ArticleIndexPage
    class by forcing all child page urls to conform to a yyyy/mm/dd/slug format. 
    
    """

    def get_context(self, request, year=None, month=None, day=None):
        # Update content to include only published posts; ordered by reverse-chronological
        context = super(ArticleIndexByDatePage, self).get_context(request)
        all_articles = self.get_children().live().order_by('-first_published_at')

        if year:
            all_articles = all_articles.filter(first_published_at__year=year)
        if month:
            all_articles = all_articles.filter(first_published_at__month=month)
        if day:
            all_articles = all_articles.filter(first_published_at__day=day)

        # get the paginator obj and the current page number
        paginator = Paginator(all_articles, self.per_page) 
        page = request.GET.get('page')
        index = int(page)-1 if page is not None else 0
        
        # get list of articles for the desired page
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)

        # limit page_range of the paginator (hard-coded to 3 pages both ways)
        max_index = len(paginator.page_range)
        start_index = max(0, index - 3)
        end_index = min(max_index, start_index + 7)

        # build new page range from calculated range but also include first/last pages if not in range
        context['page_range'] = []
        if start_index > 0:
            context['page_range'].append(1)
        context['page_range'] = context['page_range'] + list(paginator.page_range)[start_index:end_index]
        if end_index < max_index:
            context['page_range'].append(max_index)
            
        context['articles'] = articles
        context['year'] = year
        context['month'] = month
        context['day'] = day
        
        return context

    # route for sub-pages with a date specific URL for posts
    # this will NOT make a list of pages at blog/2018 just specific blogs only

    @route(r'^(?P<year>[0-9]{4})/?$')
    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/?$')
    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/?$')
    def article_index_by_date(self, request, year, month=None, day=None, name='article-index-by-date'):
        print("article_index_by_date()")
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request, year=year, month=month, day=day)
        )
    
    
    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<slug>[\w-]+)/?$')
    def article_page_by_date(self, request, year, month, day, slug, name='article-by-date'):
        """Serve a single article page at URL (eg. .../2018/01/23/my-title/)"""

        # try:
        #     article_page = self.get_children().live().specific().get(
        #         first_published_at__year=year,
        #         first_published_at__month=month,
        #         first_published_at__day=day,
        #         slug=slug)
        # except Page.DoesNotExist as e:
        #     raise Http404("Article does not exist")
        
        article_page = get_object_or_404(
            self.get_children().live().specific(),
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


    def get_template(self, request):
        return f'article/article_index_by_date_page_{self.sidebar_placement}.html'

    # Control what child pages can be created under this index page
    # To prevent multiple date/slug urls, do not allow any additional ArticleIndexByDatePage instances as children
    #   as this may produce odd urls e.g., /articles/2020/01/01/other-index/2020/01/04
    # Speficies that only ArticlePage objects can live under this index page
    
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

    ARTICLE_IMAGE_FILTERSPEC_DEFAULT='fill-1200x300'
    ARTICLE_IMAGE_FILTERSPEC_CHOICES = (
        ('fill-1200x300', 'Banner (fill-1200x300)'),
        ('fill-1200x150', 'Banner (fill-1200x150)'),
        ('max-1200x300', 'Best Fit Original (max-1200x600)'),
    )

    RENDER_TEMPLATE_DEFAULT='article_page_default'
    RENDER_TEMPLATE_CHOICES = (
        ('article_page_default', 'Default (Basic article layout)'),
        ('article_page_splash', 'Splash (Full-width banner image/content; overlay box'),
    )

    SIDEBAR_PLACEMENT_DEFAULT='left'
    SIDEBAR_PLACEMENT_CHOICES = (
        ('left', 'Single sidebar (To left of main content'),
        ('right', 'Single sidebar (To right of main content'),
        ('none', 'No sidebars'),
    )
    
    # content fields
    #   title - inherited
    
    intro = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide introductory content here. This will be used in the blog list pages and search result summaries.'),
    )

    body = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide the main body content here. This is not visible in the blog list and search summaries but is still searchable.'),
    )

    # meta fields
    #   tags - inherited
    #   search_desc inherited

    author = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Use this to override the default author/owner name (free text only).'),
    )

    # promote fields
    #   slug - inherited
    #   page_title - inherited
    #   show_in_menus = inherited
    
    article_image = models.ForeignKey(
        'captioned_images.CaptionImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Provide an image that spans the top of the article content (and is used as thumbnail in the blog listings unless overridden.'),
    )

    article_image_filterspec = models.CharField(
        max_length=128,
        default=ARTICLE_IMAGE_FILTERSPEC_DEFAULT,
        choices=ARTICLE_IMAGE_FILTERSPEC_CHOICES,
    )
    
    thumbnail_image = models.ForeignKey(
        'captioned_images.CaptionImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Specify an alternative image for the thumbnail in blog listings if the main banner image is not suitable or a different image is desired.'),
    )
    
    # splash fields
    
    splash_image = models.ForeignKey(
        'captioned_images.CaptionImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Provide an image that spans the top of an article page (if splash template selected).'),
    )
    
    splash_content = StreamField(
        sitecore_blocks.SplashBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide content for the splash area here. This will be used in the blog list pages and search result summaries.'),
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

    # inset fields
    
    inset_content = StreamField(
        sitecore_blocks.SplashBlock,
        validators=[ValidateCoreBlocks],
        blank=True,
        help_text=_('Provide content for the inset area here.'),
    )

    inset_text_align = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_ALIGN_CHOICES,
        default='text-center',
        max_length=128
    )

    inset_text_colour = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        default='text-primary',
        max_length=128
    )

    inset_bg_colour = models.CharField(
        choices=constants.BOOTSTRAP4_BACKGROUND_COLOUR_CHOICES,
        default='bg-transparent',
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

    render_template = models.CharField(
        max_length=128,
        default='article_page_default',
        choices=RENDER_TEMPLATE_CHOICES,
    )

    sidebar_placement = models.CharField(
        max_length=128,
        default='left',
        choices=SIDEBAR_PLACEMENT_CHOICES,
    )

    # Append which fields are to be searchable
    
    search_fields = SitePage.search_fields + [
        index.SearchField('author'),
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('splash_content'),
        index.SearchField('inset_content'),
    ]

    # Append which fields are to be accessible via the REST API

    api_fields = SitePage.api_fields + [
        'author',
        'article_image',
        'article_image_filterspec',
        'thumbnail_image',
        'intro',
        'body',
        'display_title',
        'render_template',
        'splash_image',
        'splash_content',
        'inset_content',
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
        FieldPanel('tags'),
        FieldPanel('author'),
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
    ]

    inset_tab_panel = [
        StreamFieldPanel('inset_content'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('inset_text_align'),
                FieldPanel('inset_text_colour'),
            ]),
            FieldRowPanel([
                FieldPanel('inset_bg_colour'),
                FieldPanel('inset_border_radius'),
            ]),
            FieldPanel('inset_style'),
        ], heading=_('Inset Settings')),
    ]

    # Rebuild settings tab panel - add display/override fields
    
    settings_tab_panel = [
        ImageChooserPanel('article_image'),
        FieldPanel('article_image_filterspec'),
        ImageChooserPanel('thumbnail_image'),
        FieldPanel('render_template'),
        FieldPanel('sidebar_placement'),
    ]

    # Rebuild promote tab panel
    
    promote_tab_panel = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
            FieldPanel('display_title'),
        ], heading=_('Options')),
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
        ObjectList(inset_tab_panel, heading='Inset'),
        ObjectList(publish_tab_panel, heading='Publish'),
    ])


    def get_template(self, request):
        return f'article/{self.render_template}_{self.sidebar_placement}.html'


    def set_url_path(self, parent):
        # initially set the attribute self.url_path using the normal operation
        super().set_url_path(parent=parent)

        # only modify url if page is a child of an ArticleIndexByDatePage
        if isinstance(parent.specific,ArticleIndexByDatePage):
            if self.first_published_at:
                self.url_path = self.url_path.replace(
                    self.slug, '{:%Y/%m/%d/}'.format(self.first_published_at) + self.slug
                )
            else:
                self.url_path = self.url_path.replace(
                    self.slug, '{:%Y/%m/%d/}'.format(timezone.now()) + self.slug
                )
