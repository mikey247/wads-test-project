"""
Sitecore models module for implementing the search index page
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, PrivacyModalPanel, PublishingPanel, StreamFieldPanel, TabbedInterface
from wagtail.contrib.routable_page.models import route, RoutablePageMixin
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable, Site
from wagtail.search.models import Query

from sitecore import blocks as sitecore_blocks
from sitecore.parsers import ValidateCoreBlocks

from .sitepage import SitePage, SitePageTags


class SiteSearchIndexPage(SitePage):
    """
    This defines a search index page for searching content with given search terms
    The ?query= field in the page request is used to search for specific
    content matching the terms. As the superclass SitePage is used, content is found across all
    derived models.
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
        help_text=_('(Optional) Provide introductory text here to describe the search index.'),
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
    
    # Build new meta tab panel
    
    # Rebuild main content tab panel
    
    content_tab_panel = [
        FieldPanel('title'),
        StreamFieldPanel('intro')
    ]

    # Rebuild promote tab panel
    
    promote_tab_panel = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
        ], heading=_('Options')),
    ]

    settings_tab_panel = [
        FieldPanel('per_page'),
        FieldPanel('sidebar_placement'),
        MultiFieldPanel([
            FieldPanel('display_title'),
            FieldPanel('display_intro'),
        ], heading='Options'),
    ]

    publish_tab_panel = [
        PublishingPanel(),
        PrivacyModalPanel(),
    ]

    # Rebuild edit_handler so we have all tabs
    
    edit_handler = TabbedInterface([
        ObjectList(content_tab_panel, heading='Content'),
        ObjectList(promote_tab_panel, heading='Promote'),
        ObjectList(settings_tab_panel, heading='Settings'),
        ObjectList(publish_tab_panel, heading='Publish'),
    ])


    def get_context(self, request, slug=None):
        context = super(SiteSearchIndexPage, self).get_context(request)

        # (1) Retrieve all pages that match search terms
        search_terms = request.GET.get('query', None)

        if search_terms:
            search_query = Query.get(search_terms)
            results_all = SitePage.objects.live().specific().order_by('-first_published_at').search(search_terms)
            results_count = len(results_all)
            url_params = f'query={search_terms}'
            # Record hit
            search_query.add_hit()
        else:
            results_all = SitePage.objects.none()
            results_count = 0
            url_params = ''

        # (2) If we have some results, paginate them based on model settings
        if results_all is not None:
            paginator = Paginator(results_all, self.per_page)
            page_num = request.GET.get('page', 1)
            page_index = int(page_num)-1 if page_num is not None else 0
        
            # get list of results for the desired paginator page
            try:
                results_paginated = paginator.page(page_num)
            except PageNotAnInteger:
                results_paginated = paginator.page(1)
            except EmptyPage:
                results_paginated = paginator.page(paginator.num_pages)

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
        else:
            results_paginated = None
            context['paginator_count'] = 0
            context['paginator_range'] = None

        # (3) Return paginated results
        context['search_terms'] = search_terms
        context['results_paginated'] = results_paginated
        context['results_count'] = results_count
        context['url_params'] = url_params
        
        return context

    
    # render template

    template = 'sitecore/search/index_page.html'
