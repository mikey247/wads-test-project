
from django.contrib import admin

from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)

from .models import EventPage


@admin.display(description='Event Type')
def event_type_name(obj):
    """
    Custom modeladmin display option to retrieve event type as name
    As event type is defined within a streamblock, we get its block name
    Note: event_type streamfield is limited to ONE instance and is a 
    required field.
    """
    return f'{obj.event_type[0].block.label}'


class EventTypeListFilter(admin.SimpleListFilter):
    """
    
    """
    title = 'Event Type'
    parameter_name = 'event_type'

    def lookups(self, request, model_admin):
        return (
            ('registration', 'Registration'),
            ('open_meeting', 'Open Meeting'),
        )

    def queryset(self, request, queryset):
        if self.value():
            try:
                event_type_name = str(self.value())
            except (ValueError):
                return queryset.none()
            else:
                return queryset.filter(event_type_name=event_type_name)

                

class EventPageWagtailAdmin(ModelAdmin):
    """
    Create a ModelAdmin for handling Events in Wagtail Admin

    This will remove all events (EventPage instances) from the Page Explorer menu
    using 'exclude_from_explorer' and instead list them in a new main admin menu

    Events are ordered by reverse start date, so most recent at the top
    The filters includes the EventTypeList filter defined above
    The list includes a column for the event_type_name as defined above
    """
    model = EventPage
    menu_label = 'Events'  # ditch this to use verbose_name_plural from model
    menu_icon = 'date'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = True # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title', event_type_name, 'author', 'start_date', 'first_published_at')
    list_export = ('title', 'author', 'first_published_at')
    list_filter = (EventTypeListFilter, 'start_date', 'author', 'first_published_at')
    search_fields = ('title', 'author', 'intro')
    ordering = ['-start_date']

    
# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(EventPageWagtailAdmin)

