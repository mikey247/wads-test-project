from django.db import models

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailadmin.edit_handlers import TabbedInterface, ObjectList, FieldPanel
from wagtail.wagtailcore.models import Page, Orderable

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

@register_setting
class SiteSettings(BaseSetting):

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
    content_object = ParentalKey('SitePage', related_name='tagged_site_pages')


class SitePage(Page):
    tags = ClusterTaggableManager(through=SitePageTags, blank=True)

    api_fields = Page.search_fields + [
        'tags',
    ]

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
    ]


class TagIndexPage(Page):
    
    def get_context(self, request):

        tag = request.GET.get('tag')
        context = super(TagIndexPage, self).get_context(request)

        pages = SitePage.objects.filter(tags__name=tag)
        tags = Tag.objects.annotate(num_tags=models.Count('sitecore_sitepagetags_items'))

        context['pages'] = pages
        context['tags'] = tags
            
        return context


