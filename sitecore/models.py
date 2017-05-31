"""
Sitecore models module for implementing site settings, a shared tag cloud cluster,
a superclass SitePage model to share commonalities, and support for tag indexing.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django.db import models

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailadmin.edit_handlers import TabbedInterface, ObjectList, FieldPanel
from wagtail.wagtailcore.models import Page, Orderable

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

@register_setting
class SiteSettings(BaseSetting):
    """
    This registers new site settings options (per site) in the Wagtail admin panels.
    Limited functionality is provided here to set the (Bootstrap 3) theme.
    Settings can be grouped and provided with tabbed panels for display.
    """
    def get_context(self, request):
        context = super(SiteSettings, self).get_context(request)
        context['site_settings'] = self.for_site(request.site)
        return context

    class Meta:
        verbose_name = 'Custom Site Settings'

    # Theme settings
    DEFAULT = 'default'
    PAPER = 'paper'
    THEME_CHOICES = (
        (DEFAULT, 'Default Bootstrap 3'),
        (PAPER, 'Bootswatch: Paper'),
    )
    bootstrap_theme = models.CharField(
        max_length = 10,
        choices=THEME_CHOICES,
        help_text='Select Bootstrap 3 Theme',
        default=PAPER
    )

    # Social media settings
    twitter = models.URLField(blank=True, help_text='Twitter Account')

    # create the panels
    theme_tab_panel = [
        FieldPanel('bootstrap_theme'),
    ]

    social_tab_panel = [
        FieldPanel('twitter'),
    ]

    # Combine into tabbed panel interface
    edit_handler = TabbedInterface([
        ObjectList(theme_tab_panel, heading='Theme'),
        ObjectList(social_tab_panel, heading='Social Media'),
    ])


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
    tags = ClusterTaggableManager(through=SitePageTags, blank=True)

    api_fields = Page.search_fields + [
        'tags',
    ]

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
    ]


class TagIndexPage(Page):
    """
    This defines a tag index page for searching content with specific tags and/or displaying the 
    entire shared tag cloud. The ?tag= field in the page request is used to search for specific
    content matching the tag. As the superclass SitePage is used, content is found across all
    derived models. All tags are returned for tag cloud rendering. Additionally the tag usage count
    is appended to the results.
    """
    
    def get_context(self, request):

        tag = request.GET.get('tag')
        context = super(TagIndexPage, self).get_context(request)

        pages = SitePage.objects.filter(tags__name=tag)
        tags = Tag.objects.annotate(num_tags=models.Count('sitecore_sitepagetags_items'))

        context['pages'] = pages
        context['tags'] = tags
            
        return context


