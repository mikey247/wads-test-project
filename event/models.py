from __future__ import absolute_import, unicode_literals

import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
 
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from sitecore import blocks as sitecore_blocks
from sitecore.fields import MarkdownShortcodeCharField, ShortcodeRichTextField
from sitecore.models import SitePage
from sitecore.parsers import ParseMarkdownAndShortcodes, ValidateCoreBlocks

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase


class EventIndexPage(Page):
    desc = ShortcodeRichTextField(blank=True)
    
    per_page = models.PositiveSmallIntegerField(default=10,
                                                validators=[
                                                    MinValueValidator(1),
                                                    MaxValueValidator(100)
                                                ])

    # Events Date Filter Options
    
    EVENTS_FILTER_PAST = 'past'
    EVENTS_FILTER_PAST_AND_CURRENT = 'past_current'
    EVENTS_FILTER_FUTURE = 'future'
    EVENTS_FILTER_CURRENT_AND_FUTURE = 'current_future'

    EVENTS_FILTER_DEFAULT = EVENTS_FILTER_CURRENT_AND_FUTURE

    EVENTS_FILTER_CHOICES = (
        (EVENTS_FILTER_CURRENT_AND_FUTURE, 'Current and Future Events'),
        (EVENTS_FILTER_FUTURE, 'Future Events'),
        (EVENTS_FILTER_PAST_AND_CURRENT, 'Past and Current Events'),
        (EVENTS_FILTER_PAST, 'Past Events'),
    )

    events_date_filter = models.CharField(
        max_length=32,
        choices=EVENTS_FILTER_CHOICES,
        help_text='Select how to filter events by date on this index listing page.',
        default=EVENTS_FILTER_DEFAULT
    )

    # Events Date Order Options

    EVENTS_ORDER_START_REV = '-start_date'
    EVENTS_ORDER_START = 'start_date'
    EVENTS_ORDER_END_REV = '-end_date'
    EVENTS_ORDER_END = 'end_date'

    EVENTS_ORDER_DEFAULT = EVENTS_ORDER_START_REV
    
    EVENTS_ORDER_CHOICES = (
        (EVENTS_ORDER_START_REV, 'Event Start Date (Reverse)'),
        (EVENTS_ORDER_START, 'Event Start Date'),
        (EVENTS_ORDER_END_REV, 'Event End Date (Reverse)'),
        (EVENTS_ORDER_END, 'Event End Date'),
    )

    events_date_order = models.CharField(
        max_length=32,
        choices=EVENTS_ORDER_CHOICES,
        help_text='Select how to sort events by start/end date on filtered events',
        default=EVENTS_ORDER_DEFAULT
    )

    index_root_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    listing_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    display_title = models.BooleanField(default=True)
    display_desc = models.BooleanField(default=False)

    no_listing_text = ShortcodeRichTextField(blank=True)

    
    def get_context(self, request):
        # Update content to include only published events; ordered by reverse-date

        # TODO: filter on current/future events
        # TODO: Build separate past event list
        
        context = super(EventIndexPage, self).get_context(request)
        # doesn't work:
        # all_events = self.get_children().live().specific().order_by('-end_date')
        # does work:
        # all_events = EventPage.objects.live().child_of(self).order_by('-start_date')

        event_order = self.events_date_order
        today = datetime.date.today()
        if self.index_root_page:
            index_root = self.index_root_page
        else:
            index_root = self
            
        if self.events_date_filter == self.EVENTS_FILTER_CURRENT_AND_FUTURE:
            all_events = EventPage.objects.live().child_of(index_root).filter(end_date__gte=today).order_by(event_order)

        elif self.events_date_filter == self.EVENTS_FILTER_FUTURE:
            all_events = EventPage.objects.live().child_of(index_root).filter(start_date__gt=today).order_by(event_order)
            
        elif self.events_date_filter == self.EVENTS_FILTER_PAST_AND_CURRENT:
            all_events = EventPage.objects.live().child_of(index_root).filter(start_date__lte=today).order_by(event_order)

        else: # self.EVENTS_FILTER_PAST
            all_events = EventPage.objects.live().child_of(index_root).filter(end_date__lt=today).order_by(event_order)


        paginator = Paginator(all_events, self.per_page) 

        page = request.GET.get('page')
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)

        context['events'] = events

        return context

    content_panels = Page.content_panels + [
        FieldPanel('desc', classname="full"),
        FieldPanel('per_page'),
        FieldPanel('events_date_filter'),
        FieldPanel('events_date_order'),
        PageChooserPanel('index_root_page', 'event.EventIndexPage'),
    ]

    promote_panels = Page.promote_panels + [
        ImageChooserPanel('listing_image'),
        MultiFieldPanel([
            FieldPanel('display_title'),
            FieldPanel('display_desc'),
            FieldPanel('no_listing_text', classname="full"),
        ], heading='Page Display Options'),
    ]
    

class EventDateTimeBlock(blocks.StructBlock):
    """Documentation for EventDateTimeBlock

        """
    date = blocks.DateBlock(
        required=True,
        help_text=_('')
    )
    
    start_time = blocks.TimeBlock(
        required=True,
        help_text=_('')
    )
    
    end_time = blocks.TimeBlock(
        required=True,
        help_text=_('')
    )
    

    class Meta:
        icon = 'date'
        template = 'datetime.html'

            
class EventTypeRegistrationBlock(blocks.StructBlock):
    """
    This structured block holds details for an event requiring registration.
    """

    details = blocks.CharBlock(
        max_length=4096,
        required=True,
        group='Registration Info and Links',
        help_text=_('Enter details of the registration process.')
    )

    link = blocks.URLBlock(
        required=False,
        group='Registration Info and Links',
        help_text=_('Enter link to the registration site.')
    )

    email = blocks.EmailBlock(
        required=False,
        group='Registration Info and Links',
        help_text=_('Enter email address to request registration.')
    )

    opening_date = blocks.DateBlock(
        required=False,
        group='Registration Important Dates',
        default=datetime.date.today,
        help_text=_('Enter the date registration opens.')
    )

    closing_date = blocks.DateBlock(
        required=False,
        group='Registration Important Dates',
        default=datetime.date.today,
        help_text=_('Enter the date registration closes.')
    )

    not_yet_open_text = blocks.CharBlock(
        max_length=255,
        required=True,
        group='Registration Status',
        default=u'Registration is not yet open',
        help_text=_('Text displayed before registration opens.')
    )
    
    open_text = blocks.CharBlock(
        max_length=255,
        required=True,
        group='Registration Status',
        default=u'Registration is open',
        help_text=_('Text displayed while registration is still open.')
    )
        
    closing_soon_text = blocks.CharBlock(
        max_length=255,
        required=True,
        group='Registration Status',
        default=u'Registration is closing soon',
        help_text=_('Text displayed one week before registration closes.')
    )
    
    closed_text = blocks.CharBlock(
        max_length=255,
        required=True,
        group='Registration Status',
        default=u'Registration is NOW CLOSED',
        help_text=_('Text displayed after registration closing date has passed.')
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        value['is_not_yet_open'] = value['opening_date'] > datetime.date.today()
        value['closed'] = value['closing_date'] < datetime.date.today()
        value['closing_soon'] = value['closing_date'] < (datetime.date.today() + datetime.timedelta(weeks=1))

        return context

    class Meta:
        icon = 'date'

    
class EventTypeOpenMeetingBlock(blocks.StructBlock):
    """
    This structured block holds details for an open meeting event
    """

    details = blocks.CharBlock(
        max_length=4096,
        required=True,
        help_text=_('Enter details of the open meeting.')
    )

    link = blocks.URLBlock(
        required=False,
        group='Open Meeting Info and Links',
        help_text=_('Enter link to additional information about the open meeting.')
    )

    email = blocks.EmailBlock(
        required=False,
        group='Open Meeting Info and Links',
        help_text=_('Enter email address to request further details.')
    )



class EventTypeBlock(blocks.StreamBlock):
    registration = EventTypeRegistrationBlock(template='event/registration.html')
    open_meeting = EventTypeOpenMeetingBlock(template='event/open_meeting.html')
    
    class Meta:
        icon='cogs'


class EventPageForm(WagtailAdminPageForm):
    def save(self, commit=True):
        page = super().save(commit=False)

        # Determine first_date and last_date from dates block
        extracted_dates = []
        for block in page.dates:
            if block.block_type == 'date_block':
                extracted_dates.append(block.value['date'])
        
        page.start_date = min(extracted_dates)
        page.end_date = max(extracted_dates)

        # Determine duration
        page.duration = (page.end_date - page.start_date).days + 1

        if commit:
            page.save()
        return page


class EventPage(SitePage):

    # New event fields

    # title (SitePage)
    # tags (SitePage)
    # ---------------------------------------
    # author
    # intro
    # event_image
    # datetimes
    #   ListBlock
    #     StructBlock
    #       date
    #       start_time
    #       end_time
    # (closing_date) <= max(dates)
    # location
    # location link
    # document(s)
    #   ListBlock
    #     DocumentChooser
    # body
    # registration (text, link, closing date)
    #   StructBlock
    #     open_text
    #     closed_text
    #     link
    #      reg_closing_date
    # agenda (table)
    #   Snippet?
    #     Table Options
    #     Text field (CSV?)
    # ---------------------------------------

    # Form Model fields
    
    author = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Use this to override the default author/owner name.')
    )

    intro = ShortcodeRichTextField(
        blank=True,
        help_text=_('Provide introductory text here to summarise the event. Content appears in the event listing page and search result summaries.')
    )

    # intro = models.CharField(
    #     max_length=4096,
    #     blank=True,
    #     help_text=_('Provide introductory text here to summarise the event. Content appears in the event listing page and search result summaries.')
    # )

    event_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    location = models.CharField(
        max_length=255,
        blank=False,
        help_text=_('Location of the event')
    )

    location_link = models.URLField(
        blank=True,
        help_text=_('Link to location/institution website')
    )

    body = StreamField(
        sitecore_blocks.CoreBlock,
        validators=[ValidateCoreBlocks]
    )

    dates = StreamField([
        ('date_block', EventDateTimeBlock(),),
    ])

    event_type = StreamField(
        EventTypeBlock(max_num=1, min_num=1, required=True)
    )
    
    # Model Only fields - generated and saved in EventPageForm.save()

    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.IntegerField()

    # Model view methods - callable in template views for EventPage and EventIndexPage - preferred over context['name']
    
    def running(self):
        return (self.start_date <= datetime.date.today()) & (datetime.date.today() <= self.end_date)

    def passed(self):
        return (self.end_date < datetime.date.today())

    def in_same_month(self):
        return (self.start_date.month == self.end_date.month) & (self.start_date.year == self.end_date.year)
    
    # Search and API
    
    search_fields = SitePage.search_fields + [
        index.SearchField('author'),
        index.SearchField('intro'),
        index.SearchField('location'),
        index.SearchField('body'),
        index.SearchField('dates'),
        index.SearchField('event_type'),
        index.FilterField('start_date'),
        index.FilterField('end_date'),
    ]

    api_fields = SitePage.search_fields + [
        'author',
        'intro',
        'location',
        'location_link',
        'body',
        'dates',
        'event_type',
    ]

    # Admin UI panels
    
    content_panels = SitePage.content_panels + [
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('intro'),
            FieldPanel('location'),
            FieldPanel('location_link'),
            StreamFieldPanel('dates'),
            StreamFieldPanel('event_type'),
        ], heading="Event Details"),
        MultiFieldPanel([
            StreamFieldPanel('body')
        ], heading="Main body (Streamfield)"),
    ]

    promote_panels = SitePage.promote_panels + [
        ImageChooserPanel('event_image'),
    ]

    # base_form_class:
    # Use the override base_form_class for additional non-form model fields.
    #   start_date, end_date and duration
    # - These fields are available in EventPage and its templates *but also* to EventIndexPage and its templates
    # - These fields are only modified on save() by this form - so it's not possible to refer to live values e.g., today()

    base_form_class = EventPageForm
    
    # get_context:
    # Include additional values to the EventPage template context upon live rendering.
    #   (start/end dates) in_same_month, (event) running and (event) passed

    def get_context(self, request):
        context = super(EventPage, self).get_context(request)

        # LML: context['name'] entries do work but only when rendering the EventPage directly
        # Context entries are *not* included on events resulting from the EventIndexPage queryset filters
        # Preferred method now is to define these as view methods e.g., EventPage: def running():
        
        # use the extracted start/end dates and determine if they're in the same month
        #context['in_same_month'] = (self.start_date.month == self.end_date.month) & (self.start_date.year == self.end_date.year)

        # Flag if event is running or has already taken place
        #context['running'] = (self.start_date <= datetime.date.today()) & (datetime.date.today() <= self.end_date) 
        #context['passed'] = (self.end_date < datetime.date.today())
        
        return context
    
