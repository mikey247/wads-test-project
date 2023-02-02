from __future__ import absolute_import, unicode_literals

import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
 
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, PageChooserPanel, PrivacyModalPanel, PublishingPanel,  TabbedInterface
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.search import index

from sitecore import blocks as sitecore_blocks
from sitecore.models import SitePage


class EventIndexPage(SitePage):

    intro = StreamField(
        sitecore_blocks.CoreBlock,
        blank=True,
        help_text=_('Provide introductory content here. This will be used in the Event list pages and search result summaries.'),
        verbose_name='Intro',
        use_json_field=True
    )

    per_page = models.PositiveSmallIntegerField(default=10,
                                                verbose_name='Events per Page',
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
        'sitecore.SiteImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    display_title = models.BooleanField(
        default=True,
        verbose_name='Display Title'
    )

    display_intro = models.BooleanField(
        default=False,
        verbose_name='Display Intro'
    )

    no_listing_text = RichTextField(
        blank=True,
        verbose_name='No Listing Text',
        help_text='Warning text to display when there are no events that can be listed.',
    )

    def get_context(self, request):
        # Update content to include only published events; ordered by reverse-date
        context = super().get_context(request)

        event_order = self.events_date_order
        today = datetime.date.today()
        if self.index_root_page:
            index_root = self.index_root_page
        else:
            index_root = self

        if self.events_date_filter == self.EVENTS_FILTER_CURRENT_AND_FUTURE:
            events_all = EventPage.objects.live().child_of(index_root).filter(end_date__gte=today).order_by(event_order)

        elif self.events_date_filter == self.EVENTS_FILTER_FUTURE:
            events_all = EventPage.objects.live().child_of(index_root).filter(start_date__gt=today).order_by(event_order)

        elif self.events_date_filter == self.EVENTS_FILTER_PAST_AND_CURRENT:
            events_all = EventPage.objects.live().child_of(index_root).filter(start_date__lte=today).order_by(event_order)

        else:  # self.EVENTS_FILTER_PAST
            events_all = EventPage.objects.live().child_of(index_root).filter(end_date__lt=today).order_by(event_order)

        events_count = len(events_all)

        # get the paginator obj and the current page number
        paginator = Paginator(events_all, self.per_page)
        page_num = request.GET.get('page')
        page_index = int(page_num) - 1 if page_num is not None else 0

        # get list of events for the desired page
        try:
            events_paginated = paginator.page(page_num)
        except PageNotAnInteger:
            events_paginated = paginator.page(1)
        except EmptyPage:
            events_paginated = paginator.page(paginator.num_pages)

        # limit page_range of the paginator (hard-coded to 3 pages both ways)
        page_index_max = len(paginator.page_range)
        page_index_start = max(0, page_index - 3)
        page_index_end = min(page_index_max, page_index_start + 7)

        # build new paginator ange from calculated range but also include first/last pages if not in range
        context['paginator_range'] = []
        if page_index_start > 0:
            context['paginator_range'].append(1)
        context['paginator_range'] = context['paginator_range'] + list(paginator.page_range)[page_index_start:page_index_end]
        if page_index_end < page_index_max:
            context['paginator_range'].append(page_index_max)

        context['paginator_count'] = paginator.num_pages
        context['events_count'] = events_count
        context['events_paginated'] = events_paginated

        return context

    content_tab_panel = [
        FieldPanel('title'),
        FieldPanel('listing_image'),
        FieldPanel('intro'),
    ]

    promote_tab_panel = [
        FieldPanel('slug'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
        ], heading=_('Options')),
    ]

    settings_tab_panel = [
        MultiFieldPanel([
            FieldPanel('no_listing_text'),
            FieldPanel('per_page'),
            FieldPanel('events_date_filter'),
            FieldPanel('events_date_order'),
            PageChooserPanel('index_root_page', 'event.EventIndexPage'),
            # LML can't replace PageChooserPanel if it uses a root page argument
            # FieldPanel('index_root_page', 'event.EventIndexPage'),
        ], heading='Listing Display Options'),
        MultiFieldPanel([
            FieldPanel('display_title'),
            FieldPanel('display_intro'),
        ], heading='Page Options'),
    ]

    publish_tab_panel = [
        PublishingPanel(),
        PrivacyModalPanel(),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_tab_panel, heading='Content'),
        ObjectList(promote_tab_panel, heading='Promote'),
        ObjectList(settings_tab_panel, heading='Settings'),
        ObjectList(publish_tab_panel, heading='Publish'),
    ])

    # restrict page types that can lie under an EventIndexPage
    subpage_types = ['event.EventPage', 'event.EventIndexPage']


class EventDateTimeBlock(blocks.StructBlock):
    """
    Documentation for EventDateTimeBlock
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
        help_text=_('Enter the date registration opens.')
    )

    closing_date = blocks.DateBlock(
        required=False,
        group='Registration Important Dates',
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
    
    def clean(self, value):
        errors = {}
        # Check opening date is before closing date, if provided
        if value.get('opening_date') and value.get('closing_date') and value.get('opening_date') > value.get('closing_date'):
            errors['closing_date'] = ErrorList(['The closing date cannot be before the opening date.'])
            errors['opening_date'] = ErrorList(['The closing date cannot be before the opening date.'])
        if errors:
            raise ValidationError("Bad closing date", params=errors)
        return super().clean(value)


    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        if value['opening_date']:
            value['is_not_yet_open'] = value['opening_date'] > datetime.date.today()
        else:
            if not value['closing_date']:
                value['is_not_yet_open'] = True
            else:
                value['is_not_open_yet'] = False
        
        if value['closing_date']:
            value['closed'] = value['closing_date'] < datetime.date.today()
            value['closing_soon'] = value['closing_date'] < (datetime.date.today() + datetime.timedelta(weeks=1))
        else:
            value['closed'] = False
            value['closing_soon'] = False
        

        return context

    class Meta:
        icon = 'clipboard-list'
        label = 'Registration'

    
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

    class Meta:
        icon = 'group'
        label = 'Open Meeting'


class EventTypeBlock(blocks.StreamBlock):
    registration = EventTypeRegistrationBlock(template='event/registration.html')
    open_meeting = EventTypeOpenMeetingBlock(template='event/open_meeting.html')
    
    class Meta:
        icon = 'cogs'


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

        # Determine simple event type name for ModelAdmin filtering
        block = page.event_type[0].block
        page.event_type_name = block.name

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

    intro = RichTextField(
        blank=True,
        help_text=_('Provide introductory text here to summarise the event. Content appears in the event listing page and search result summaries.')
    )

    # intro = models.CharField(
    #     max_length=4096,
    #     blank=True,
    #     help_text=_('Provide introductory text here to summarise the event. Content appears in the event listing page and search result summaries.')
    # )

    event_image = models.ForeignKey(
        'sitecore.SiteImage',
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
        use_json_field=True
    )

    dates = StreamField(
        [('date_block', EventDateTimeBlock(),)],
        use_json_field=True)

    event_type = StreamField(
        EventTypeBlock(max_num=1, min_num=1, required=True),
        use_json_field=True
    )
    
    # Model Only fields - generated and saved in EventPageForm.save()

    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.IntegerField()
    event_type_name = models.CharField(
        max_length=255,
        blank=False,
    )

    # Model view methods - callable in template views for EventPage and EventIndexPage - preferred over context['name']
    
    def running_today(self):
        return (self.start_date <= datetime.date.today()) & (datetime.date.today() <= self.end_date)

    # Addittional context methods - preferred in context so only called once per page view
    
    def get_today_state(self):
        now_datetime = datetime.datetime.today()
        now_date = now_datetime.date()
        now_time = now_datetime.time()
        if (self.start_date <= now_date) & (now_date <= self.end_date):
            for day in self.dates:
                if day.value['date'] == now_date:
                    state = {
                        'message': '',
                        'start_time': day.value['start_time'],
                        'end_time': day.value['end_time'],
                        'now': now_datetime,
                    }

                    if (day.value['start_time'] <= now_time) & (now_time <= day.value['end_time']):
                        state['message'] = "Today's event is taking place right now"
                    elif now_datetime < (datetime.datetime.combine(day.value['date'], day.value['start_time']) - datetime.timedelta(hours=1)):
                        state['message'] = "The event starts later today"
                    elif now_time < day.value['start_time']:
                        state['message'] = "Today's event starts soon"
                    elif now_time > day.value['end_time']:
                        if day.value['date'] < self.end_date:
                            state['message'] = "The event has finished for today but continues tomorrow"
                        else:
                            state['message'] = "The event has now closed"

                    return state
        # no matching date blocks found
        return None
 
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

    content_tab_panel = SitePage.content_panels + [
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('event_image'),
            FieldPanel('intro'),
            FieldPanel('location'),
            FieldPanel('location_link'),
            FieldPanel('dates'),
            FieldPanel('event_type'),
        ], heading="Event Details"),
            FieldPanel('body')
    ]

    promote_tab_panel = SitePage.promote_panels

    publish_tab_panel = [
        PublishingPanel(),
        PrivacyModalPanel(),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_tab_panel, heading='Content'),
        ObjectList(promote_tab_panel, heading='Promote'),
        ObjectList(publish_tab_panel, heading='Publish'),
    ])

    # base_form_class:
    # Use the override base_form_class for additional non-form model fields.
    #   start_date, end_date and duration
    # - These fields are available in EventPage and its templates *but also* to EventIndexPage and its templates
    # - These fields are only modified on save() by this form - so it's not possible to refer to live values e.g., today()

    base_form_class = EventPageForm

    # restrict page types that can lie under an EventPage
    subpage_types = ['article.ArticlePage']
    parent_page_types = ['event.EventIndexPage']

    # get_context:
    # Include additional values to the EventPage template context upon live rendering.
    #   (start/end dates) in_same_month, (event) running and (event) passed

    def get_context(self, request):
        context = super().get_context(request)

        # Add some context about the event if running today
        context['today_state'] = self.get_today_state()

        return context
