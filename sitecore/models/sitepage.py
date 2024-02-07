"""
Sitecore models module for implementing the superclass SitePage model to share commonalities
across all derived Page based models.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

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

    New fields:
    - 'tags' for site-wide tagging system
    - 'menu_label' for overriding text displayed in navigation menus (if title is too long)
       e.g., title="Research IT Services"; menu_label="Services"

    Inherited Page.content_panels:
    - title

    Inherited Page.promote_panels:
    - slug, seo_title, search_description, show_in_menus

    Inherited Page.settings_panels:
    - PublishingPanel()

    """

    # prevent direct creation of an "abstract" SitePage
    is_creatable = False

    # add site-wide tags to all SitePages
    tags = ClusterTaggableManager(through=SitePageTags, blank=True)

    # add menu_label override
    menu_label = models.CharField(
        max_length=32,
        default='',
        blank=True,
        help_text=_("Provide text to override the default title used to generate the menu label")
    )
    
    # pass through existing Page.search_fields
    search_fields = Page.search_fields

    # add site-wide tags to API
    api_fields = [
        'tags',
        'menu_label',
    ]

    # add site-wide tags field to content_panels
    content_panels = Page.content_panels + [
        FieldPanel('tags'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('menu_label'),
    ]
