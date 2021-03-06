from datetime import date
from django import template
from django.conf import settings

register = template.Library()

# Renders the event page summary as blog listing entry
@register.inclusion_tag('event/tags/event_blog_summary.html', takes_context=True)
def event_blog_summary(context, event, show_taggit=False, taggit_slug=''):
   return {
      'event': event,
      'show_taggit': show_taggit,
      'taggit_slug': taggit_slug,
   }
