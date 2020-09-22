"""
Sitecore models module for implementing site settings, a shared tag cloud cluster,
a superclass SitePage model to share commonalities, and support for tag indexing.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.template.response import TemplateResponse

from wagtail.contrib.routable_page.models import route, RoutablePageMixin
from wagtail.core.models import Page, Orderable, Site

from taggit.models import Tag

from .sitepage import SitePage, SitePageTags

class TagIndexPage(RoutablePageMixin, Page):
    """
    This defines a tag index page for searching content with specific tags and/or displaying the 
    entire shared tag cloud. The ?tag= field in the page request is used to search for specific
    content matching the tag. As the superclass SitePage is used, content is found across all
    derived models. All tags are returned for tag cloud rendering. Additionally the tag usage count
    is appended to the results.
    """

    template = 'sitecore/taggit/index_page.html'

    def get_context(self, request, slug=None):
        context = super(TagIndexPage, self).get_context(request)

        # Retrieve requested tag from URL
        #tag = request.GET.get('tag')

        # Retrieve all pages that match tag (if provided)
        # pages = SitePage.objects.live().filter(tags__slug=tag)
        if slug:
            pages = SitePage.objects.live().filter(tags__slug=slug).order_by('-first_published_at')
            name = Tag.objects.get(slug=slug)
        else:
            pages = SitePage.objects.live().order_by('-first_published_at')
            name = None

        # Produce tag cloud based only managed by SitePageTags (and ignore tags in other models)
        # Get tag_id of all SitePageTags; use that as filter against pk in (all) Tag.objects()
        # TODO: Probably better query to achieve this
        site_page_tag_ids = [t.tag_id for t in SitePageTags.objects.all()]
        tags = Tag.objects.filter(pk__in=site_page_tag_ids).order_by('slug').annotate(num_tags=models.Count('sitecore_sitepagetags_items'))

        # Return all matching pages and whole tag cloud
        context['pages'] = pages
        context['tags'] = tags
        context['slug'] = slug
        context['name'] = name
        
        return context

    @route(r'^(?P<slug>[\w-]+)/?$')
    def tag_index_by_slug(self, request, slug=None, name='tag-index-by-slug'):
        print("tag_index_by_slug", slug)
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request, slug=slug)
        )
