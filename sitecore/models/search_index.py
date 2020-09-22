"""
Sitecore models module for implementing the search index page
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models

from wagtail.core.models import Page, Orderable, Site
from wagtail.search.models import Query

from .sitepage import SitePage, SitePageTags


class SearchIndexPage(Page):
    """
    This defines a search index page for searching content with given search terms
    The ?query= field in the page request is used to search for specific
    content matching the terms. As the superclass SitePage is used, content is found across all
    derived models.
    """
    
    template = 'sitecore/search/index_page.html'

    def get_context(self, request, slug=None):
        context = super(SearchIndexPage, self).get_context(request)

        search_query = request.GET.get('query', None)
        page = request.GET.get('page', 1)

        # Retrieve all pages that match search terms
        # Get first query matched and add a hit?
        if search_query:
            search_results = SitePage.objects.live().specific().order_by('-first_published_at').search(search_query)
            query = Query.get(search_query)
        
            # Record hit
            query.add_hit()
        else:
            search_results = SitePage.objects.none()

        # Pagination
        paginator = Paginator(search_results, 10)
        try:
            search_results = paginator.page(page)
        except PageNotAnInteger:
                search_results = paginator.page(1)
        except EmptyPage:
            search_results = paginator.page(paginator.num_pages)
            
        # Return all matching pages and whole tag cloud
        context['pages'] = search_results
        context['query'] = search_query
        
        return context
