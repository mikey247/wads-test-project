from __future__ import absolute_import, unicode_literals

from django.contrib.humanize.templatetags.humanize import ordinal
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
 
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, PublishingPanel, TabbedInterface
from wagtail.contrib.routable_page.models import route, RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.search import index

from sitecore import blocks as sitecore_blocks
from sitecore import constants
from sitecore.models import SitePage

from article.forms import FilterForm

import logging
logger = logging.getLogger(__name__)


class ArticleIndexPage(RoutablePageMixin, SitePage):
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

    # presentation/settings choices

    SIDEBAR_PLACEMENT_DEFAULT = 'left'
    SIDEBAR_PLACEMENT_CHOICES = (
        ('left', 'Single sidebar (To left of main content)'),
        ('right', 'Single sidebar (To right of main content)'),
        ('none', 'No sidebars'),
    )

    LAYOUT_STYLE_DEFAULT = 'blog'
    LAYOUT_STYLE_CHOICES = (
        ('blog', 'Blog Listing'),
        ('card', 'Card (Style 1)'),
    )

    LISTING_ORDER_DEFAULT = 'path'
    LISTING_ORDER_CHOICES = (
        (LISTING_ORDER_DEFAULT, 'Admin Sort Order'),
        ('-path', 'Admin Sort Order (reversed)'),
        ('-first_published_at', 'Publication Date (New to Old)'),
        ('first_published_at', 'Publication Date (Old to New)'),
    )

    # additional content fields

    intro = StreamField(
        sitecore_blocks.CoreBlock,
        blank=True,
        help_text=_('Provide introductory content here. This will be used in the blog list pages and search result summaries.'),
        verbose_name='Intro',
        use_json_field=True
    )

    # presentation/settings fields

    per_page = models.PositiveSmallIntegerField(
        default=12,
        verbose_name='Articles per Page',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ])

    display_title = models.BooleanField(default=True)
    display_intro = models.BooleanField(default=False)
    display_meta = models.BooleanField(default=True)

    sidebar_placement = models.CharField(
        max_length=128,
        default=SIDEBAR_PLACEMENT_DEFAULT,
        choices=SIDEBAR_PLACEMENT_CHOICES,
    )

    layout_style = models.CharField(
        max_length=128,
        default=LAYOUT_STYLE_DEFAULT,
        choices=LAYOUT_STYLE_CHOICES,
    )

    listing_order = models.CharField(
        max_length=128,
        default=LISTING_ORDER_DEFAULT,
        choices=LISTING_ORDER_CHOICES,
    )

    default_thumbnail = models.ForeignKey(
        'sitecore.SiteImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Specify a default image for the thumbnail in blog/card listings if the child article does not have one.'),
    )

    def get_context(self, request):
        # Update content to include only published posts; ordered by reverse-chronological
        context = super().get_context(request)
        articles_all = self.get_children().live().order_by(self.listing_order)
        articles_count = len(articles_all)

        # get the paginator obj and the current page number
        paginator = Paginator(articles_all, self.per_page)
        page_num = request.GET.get('page')
        page_index = int(page_num) - 1 if page_num is not None else 0

        # get list of articles for the desired page
        try:
            articles_paginated = paginator.page(page_num)
        except PageNotAnInteger:
            articles_paginated = paginator.page(1)
        except EmptyPage:
            articles_paginated = paginator.page(paginator.num_pages)

        # limit page_range of the paginator (hard-coded to 3 pages both ways)
        page_index_max = len(paginator.page_range)
        page_index_start = max(0, page_index - 3)
        page_index_end = min(page_index_max, page_index_start + 7)

        # pass total number of pages
        context['paginator_count'] = paginator.num_pages

        # build new paginator ange from calculated range but also include first/last pages if not in range
        context['paginator_range'] = []
        if page_index_start > 0:
            context['paginator_range'].append(1)
        context['paginator_range'] = context['paginator_range'] + list(paginator.page_range)[page_index_start:page_index_end]
        if page_index_end < page_index_max:
            context['paginator_range'].append(page_index_max)

        context['paginator_count'] = paginator.num_pages
        context['articles_paginated'] = articles_paginated
        context['articles_count'] = articles_count

        return context

    # Build new meta tab panel

    # Rebuild main content tab panel

    content_tab_panel = [
        FieldPanel('title'),
        FieldPanel('intro')
    ]

    # Rebuild promote tab panel

    promote_tab_panel = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
        ], heading=_('Search Engine Options')),
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
            FieldPanel('menu_label'),
        ], heading=_('Menu Options')),
    ]

    settings_tab_panel = [
        MultiFieldPanel([
            FieldPanel('layout_style'),
            FieldPanel('sidebar_placement'),
            FieldPanel('per_page'),
            FieldPanel('listing_order'),
            FieldPanel('default_thumbnail'),
        ], heading='Layout and Listing Options'),
        MultiFieldPanel([
            FieldPanel('display_title'),
            FieldPanel('display_intro'),
        ], heading='Main Content Options'),
        MultiFieldPanel([
            FieldPanel('display_meta'),
    ], heading='Child Content Options')
    ]

    publish_tab_panel = [
        PublishingPanel(),
    ]

    # Rebuild edit_handler so we have all tabs

    edit_handler = TabbedInterface([
        ObjectList(content_tab_panel, heading='Content'),
        ObjectList(promote_tab_panel, heading='Promote'),
        ObjectList(settings_tab_panel, heading='Settings'),
        ObjectList(publish_tab_panel, heading='Publish'),
    ])

    def get_template(self, request, *args, **kwargs):
        return f'article/article_index_page_{self.layout_style}.html'


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

    filter_by_day = models.BooleanField(default=False)

    def get_context(self, request, year=None, month=None, day=None):
        # Update content to include only published posts; ordered by reverse-chronological

        context = super().get_context(request)
        articles_all = self.get_children().live().order_by(self.listing_order)

        if request.method == 'GET':
            query_dict = request.GET.copy()
            if 'page' in query_dict:
                del query_dict['page']
            url_params = query_dict.urlencode()
            if request.GET.get('filter_button'):
                year = query_dict.get('selected_date_year') 
                month = query_dict.get('selected_date_month')
                day = query_dict.get('selected_date_day')

        if year:
            articles_all = articles_all.filter(first_published_at__year=year)
        if month:
            articles_all = articles_all.filter(first_published_at__month=month)
        if day:
            articles_all = articles_all.filter(first_published_at__day=day)

        articles_count = len(articles_all)

        # LML: future upgrade
        # get count per year
        # follow that with count per month if year filter given
        # follow that with count per day if both year and month filter given

        # will require:
        # from django.db.models import Count
        # from django.db.models.functions import ExtractYear

        # get counts:
        # yearly_count = all_articles.annotate(year=ExtractYear('first_published_at')).values('year').annotate(count=Count('id')).order_by('year')

        # get the paginator obj and the current page number
        paginator = Paginator(articles_all, self.per_page)
        page_num = request.GET.get('page')
        page_index = int(page_num) - 1 if page_num is not None else 0

        # get list of articles for the desired page
        try:
            articles_paginated = paginator.page(page_num)
        except PageNotAnInteger:
            articles_paginated = paginator.page(1)
        except EmptyPage:
            articles_paginated = paginator.page(paginator.num_pages)

        # limit page_range of the paginator (hard-coded to 3 pages both ways)
        page_index_max = len(paginator.page_range)
        page_index_start = max(0, page_index - 3)
        page_index_end = min(page_index_max, page_index_start + 7)

        # pass total number of pages
        context['paginator_count'] = paginator.num_pages

        # build new paginator ange from calculated range but also include first/last pages if not in range
        context['paginator_range'] = []
        if page_index_start > 0:
            context['paginator_range'].append(1)
        context['paginator_range'] = context['paginator_range'] + list(paginator.page_range)[page_index_start:page_index_end]
        if page_index_end < page_index_max:
            context['paginator_range'].append(page_index_max)

        form = FilterForm()
        year_choices = list(self.get_children().live().order_by('-first_published_at__year').values_list('first_published_at__year', flat=True).distinct('first_published_at__year'))
        form.fields['selected_date'].widget.years = year_choices

        context['form'] = form
        context['url_params'] = url_params

        context['year'] = year
        context['month'] = form.fields['selected_date'].widget.months[int(month)] if month else month
        context['day'] = ordinal(day) if day else day

        context['articles_paginated'] = articles_paginated
        context['articles_count'] = articles_count

        return context

    # route for sub-pages with a date specific URL for posts
    # this will NOT make a list of pages at blog/2018 just specific blogs only

    @route(r'^(?P<year>[0-9]{4})/?$')
    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/?$')
    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/?$')
    def article_index_by_date(self, request, year, month=None, day=None, name='article-index-by-date'):
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request, year=year, month=month, day=day)
        )

    @route(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<slug>[\w-]+)/?$')
    def article_page_by_date(self, request, year, month, day, slug, name='article-by-date'):
        """Serve a single article page at URL (eg. .../2018/01/23/my-title/)"""

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

    def get_template(self, request, *args, **kwargs):
        return f'article/article_index_by_date_page_{self.sidebar_placement}.html'

    # Rebuild settings tab panel

    settings_tab_panel = ArticleIndexPage.settings_tab_panel + [
        MultiFieldPanel([
            FieldPanel('filter_by_day'),
            # FieldPanel('filter_by_month'),
        ], heading='Filter Options'),
    ]

    # Rebuild edit_handler so we have all tabs
    
    edit_handler = TabbedInterface([
        ObjectList(ArticleIndexPage.content_tab_panel, heading='Content'),
        ObjectList(ArticleIndexPage.promote_tab_panel, heading='Promote'),
        ObjectList(settings_tab_panel, heading='Settings'),
        ObjectList(ArticleIndexPage.publish_tab_panel, heading='Publish'),
    ])

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

    ARTICLE_IMAGE_FILTERSPEC_DEFAULT = 'fill-1200x300'
    ARTICLE_IMAGE_FILTERSPEC_CHOICES = (
        ('fill-1200x300', 'Banner (fill-1200x300)'),
        ('fill-1200x150', 'Banner (fill-1200x150)'),
        ('max-1200x300', 'Best Fit Original (max-1200x600)'),
    )

    RENDER_TEMPLATE_DEFAULT = 'article_page_default'
    RENDER_TEMPLATE_CHOICES = (
        ('article_page_default', 'Default (Basic article layout)'),
        ('article_page_splash', 'Splash (Full-width banner image/content; overlay box'),
    )

    SIDEBAR_PLACEMENT_DEFAULT = 'left'
    SIDEBAR_PLACEMENT_CHOICES = (
        ('left', 'Single sidebar (To left of main content)'),
        ('right', 'Single sidebar (To right of main content)'),
        ('none', 'No sidebars'),
    )

    # content fields
    #   title - inherited

    intro = StreamField(
        sitecore_blocks.CoreBlock,
        blank=True,
        help_text=_('Provide introductory content here. This will be used in the blog list pages and search result summaries.'),
        use_json_field=True
    )

    body = StreamField(
        sitecore_blocks.CoreBlock,
        blank=True,
        help_text=_('Provide the main body content here. This is not visible in the blog list and search summaries but is still searchable.'),
        use_json_field=True
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
        'sitecore.SiteImage',
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
        'sitecore.SiteImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Specify an alternative image for the thumbnail in blog listings if the main banner image is not suitable or a different image is desired.'),
    )

    # splash fields

    splash_image = models.ForeignKey(
        'sitecore.SiteImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Provide an image that spans the top of an article page (if splash template selected).'),
    )

    splash_content = StreamField(
        sitecore_blocks.SplashBlock,
        blank=True,
        help_text=_('Provide content for the splash area here. This will be used in the blog list pages and search result summaries.'),
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
        'search_description',
        'show_in_menus',
        'display_title',
        'render_template',
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
        FieldPanel('tags'),
        FieldPanel('author'),
    ]

    # Build new splash tab panel

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
        FieldPanel('article_image'),
        FieldPanel('article_image_filterspec'),
        FieldPanel('thumbnail_image'),
        FieldPanel('render_template'),
        FieldPanel('sidebar_placement'),
        FieldPanel('display_title'),
    ]

    # Rebuild promote tab panel

    promote_tab_panel = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
        ], heading=_('Search Engine Options')),
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
            FieldPanel('menu_label'),
        ], heading=_('Menu Options')),
    ]

    # Build new publish tab panel

    publish_tab_panel = [
        PublishingPanel(),
    ]

    # Rebuild edit_handler so we have all tabs

    edit_handler = TabbedInterface([
        ObjectList(content_tab_panel, heading='Content'),
        ObjectList(splash_tab_panel, heading='Splash'),
        ObjectList(inset_tab_panel, heading='Inset'),
        ObjectList(promote_tab_panel, heading='Promote'),
        ObjectList(meta_tab_panel, heading='Meta'),
        ObjectList(settings_tab_panel, heading='Settings'),
        ObjectList(publish_tab_panel, heading='Publish'),
    ])

    # override inherited methods

    def get_template(self, request, *args, **kwargs):
        return f'article/{self.render_template}_{self.sidebar_placement}.html'

    def set_url_path(self, parent):
        # initially set the attribute self.url_path using the normal operation
        super().set_url_path(parent=parent)

        # only modify url if page is a child of an ArticleIndexByDatePage
        if isinstance(parent.specific, ArticleIndexByDatePage):
            if self.first_published_at:
                self.url_path = self.url_path.replace(
                    self.slug, '{:%Y/%m/%d/}'.format(self.first_published_at) + self.slug
                )
            else:
                self.url_path = self.url_path.replace(
                    self.slug, '{:%Y/%m/%d/}'.format(timezone.now()) + self.slug
                )

