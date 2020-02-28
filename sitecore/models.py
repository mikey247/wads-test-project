"""
Sitecore models module for implementing site settings, a shared tag cloud cluster,
a superclass SitePage model to share commonalities, and support for tag indexing.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django.db import models
from django.template.response import TemplateResponse

from wagtail.admin.edit_handlers import FieldPanel, ObjectList, MultiFieldPanel, TabbedInterface
from wagtail.contrib.routable_page.models import route, RoutablePageMixin
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

from sitecore import constants

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

    bootstrap_theme = models.CharField(
        max_length = 32,
        choices=constants.BOOTSTRAP4_THEME_CHOICES,
        help_text='Select a Bootstrap 4 Theme for the site',
        default=constants.INITIAL_BOOTSTRAP4_THEME
    )

    code_theme = models.CharField(
        max_length = 32,
        choices=constants.PYGMENTS_THEME_CHOICES,
        help_text='Select a Pygments Theme for code blocks',
        default=constants.INITIAL_PYGMENTS_THEME
    )

    brand_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Provide an image for the navigation bar logo (preferably small).',
    )
    
    brand_icon = models.CharField(
        max_length=64,
        default='fa fa-home',
        blank=True,
        help_text='Provide the name of a Font Awesome icon (as an alternative to a logo image) to be used as the logo in the main navigation bar.',
    )

    brand_name = models.CharField(
        max_length=64,
        blank=True,
        help_text='Provide some text for the brand name next to the logo in the main navigation bar.',
    )

    navbar_expand = models.CharField(
        max_length = 2,
        choices=constants.NAVBAR_RESPONSIVE_SIZE_CHOICES,
        help_text='Select the media size at which the navbar menu collapses',
        default='lg',
    )

    navbar_text_colour_mode = models.CharField(
        max_length = 16,
        choices=constants.NAVBAR_TEXT_COLOUR_MODE,
        help_text='Select the text foreground colour mode of the navigation bar',
        default='navbar-dark',
    )
    
    navbar_background_colour = models.CharField(
        max_length = 32,
        choices=constants.BOOTSTRAP4_BACKGROUND_COLOUR_CHOICES,
        help_text='Select the background colour of the navigation bar',
        default='bg-primary',
    )
    
    navbar_outer_class = models.CharField(
        max_length = 32,
        choices=constants.NAVBAR_OUTER_CLASS,
        help_text='Select the class of the div that encloses the navbar (container for now; none for full width)',
        default=constants.NAVBAR_OUTER_CLASS_DEFAULT,
        blank=True,
    )
    
    # Social media settings
    twitter = models.URLField(blank=True, help_text='Twitter Account')

    # create the panels
    theme_tab_panel = [
        MultiFieldPanel([
            FieldPanel('bootstrap_theme'),
            FieldPanel('code_theme'),
        ], heading="Site Themes"),
        MultiFieldPanel([
            ImageChooserPanel('brand_logo'),
            FieldPanel('brand_icon'),
            FieldPanel('brand_name'),
        ], heading="Navbar Brand"),
        MultiFieldPanel([
            FieldPanel('navbar_expand'),
            FieldPanel('navbar_text_colour_mode'),
            FieldPanel('navbar_background_colour'),
            FieldPanel('navbar_outer_class'),
        ], heading="Navbar options"),
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

    is_creatable = False
    
    tags = ClusterTaggableManager(through=SitePageTags, blank=True)

    api_fields = Page.search_fields + [
        'tags',
    ]

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
    ]


class TagIndexPage(RoutablePageMixin, Page):
    """
    This defines a tag index page for searching content with specific tags and/or displaying the 
    entire shared tag cloud. The ?tag= field in the page request is used to search for specific
    content matching the tag. As the superclass SitePage is used, content is found across all
    derived models. All tags are returned for tag cloud rendering. Additionally the tag usage count
    is appended to the results.
    """
    
    def get_context(self, request, slug=None):
        context = super(TagIndexPage, self).get_context(request)

        # Retrieve requested tag from URL
        #tag = request.GET.get('tag')

        # Retrieve all pages that match tag (if provided)
        # pages = SitePage.objects.live().filter(tags__slug=tag)
        if slug:
            pages = SitePage.objects.live().filter(tags__slug=slug)
        else:
            pages = SitePage.objects.live()

        # Produce tag cloud based only managed by SitePageTags (and ignore tags in other models)
        # Get tag_id of all SitePageTags; use that as filter against pk in (all) Tag.objects()
        # TODO: Probably better query to achieve this
        site_page_tag_ids = [t.tag_id for t in SitePageTags.objects.all()]
        tags = Tag.objects.filter(pk__in=site_page_tag_ids).annotate(num_tags=models.Count('sitecore_sitepagetags_items'))

        # Return all matching pages and whole tag cloud
        context['pages'] = pages
        context['tags'] = tags
        context['slug'] = slug
        
        return context

    @route(r'^(?P<slug>[\w-]+)/?$')
    def tag_index_by_slug(self, request, slug=None, name='tag-index-by-slug'):
        print("tag_index_by_slug", slug)
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request, slug=slug)
        )

