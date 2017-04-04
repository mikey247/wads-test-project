import shortcodes
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from sitecore.models import SiteSettings

def ParseShortcodes(value, context):
    settings = context['settings']['sitecore']['sitesettings']
    parser = shortcodes.Parser(start=settings.shortcode_start, end=settings.shortcode_end, esc=settings.shortcode_esc)
    try:
        return mark_safe(parser.parse(mark_safe(value), context))
    except shortcodes.InvalidTagError:
        raise ValidationError(
            _('Invalid shortcode tag(s) detected, please correct.'),
            params={'value':value},
        )


