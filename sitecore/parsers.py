import shortcodes
import sitecore.config as sitecore_config
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


def ParseShortcodes(value):
    parser = shortcodes.Parser(start=sitecore_config.START, end=sitecore_config.END, esc=sitecore_config.ESC)
    try:
        return mark_safe(parser.parse(mark_safe(value)))
    except shortcodes.InvalidTagError:
        raise ValidationError(
            _('Invalid shortcode tag(s) detected, please correct.'),
            params={'value':value},
        )
    
