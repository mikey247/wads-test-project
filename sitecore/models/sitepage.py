"""
Sitecore models module for implementing the superclass SitePage model to share commonalities
across all derived Page based models.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

# LML: left here while dependencies are refined per models/*.py

#from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
#from django.db import models
#from django.template.response import TemplateResponse
#from wagtail.contrib.routable_page.models import route, RoutablePageMixin
#from wagtail.contrib.settings.models import BaseSetting, register_setting
#from wagtail.images.edit_handlers import ImageChooserPanel
#from wagtail.search.models import Query
#from sitecore import constants


from wagtail.admin.edit_handlers import FieldPanel, ObjectList, MultiFieldPanel, TabbedInterface
from wagtail.core.models import Page, Orderable, Site

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from taggit.models import Tag, TaggedItemBase


class SitePageTags(TaggedItemBase):
    """
    This creates a shared tag cloud Cluster for use across all pages derived from the shared
    superclass SitePage model. This should be used for all general tag terms used across the site.
    Note: derived/other models can add separate tag clusters for maintaining separate/limited
    dictionaries of terms.
    """
    content_object = ParentalKey('SitePage', related_name='tagged_site_pages')


class SitePage(Page):
    """
    Creates a new superclass SitePage derived from the Wagtail default Page model. This enables
    the shared tag cluster to be established across all derived page models.
    Note: while this is not an abstract class (as that breaks the tag functionality) this page
    model would not normally be instanced as itself.
    """

    is_creatable = False
    
    tags = ClusterTaggableManager(through=SitePageTags, blank=True)

    search_fields = Page.search_fields
    
    api_fields = [
        'tags',
    ]

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
    ]

