import shortcodes
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

def ValidateShortcodes(value):
    parser = shortcodes.Parser(start="[[", end="]]", esc="\\")
    try:
        return parser.parse(value, context=None)
    except shortcodes.InvalidTagError:
        raise ValidationError(
            _('Invalid shortcode tag(s) detected, please correct.'),
            params={'value':value},
        )


