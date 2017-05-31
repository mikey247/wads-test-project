"""
Sitecore parser module for implementing embedded shortcodes in user entered text fields.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

import shortcodes
import sitecore.config as sitecore_config
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


def ParseShortcodes(value):
    """
    This is the both the output parser AND validator used in the ShortcodeRichText Block/Field objects. On
    Save Draft/Publish, the content of those fields will be run through this parser to determine if the
    provided content contains valid shortcodes. Invalid shortcodes will raise exceptions in the page render
    process and return a 500 page error. On page render, this parser is used to generate the output HTML,
    and has therefore already been validated.
    """
    parser = shortcodes.Parser(start=sitecore_config.START, end=sitecore_config.END, esc=sitecore_config.ESC)
    try:
        return mark_safe(parser.parse(mark_safe(value)))
    except shortcodes.InvalidTagError:
        raise ValidationError(
            _('Invalid shortcode tag(s) detected, please correct.'),
            params={'value':value},
        )
    except shortcodes.RenderingError as e:
        raise ValidationError(
            _('Invalid shortcode tag(s) detected, please correct. Details: %s' % str(e)),
            params={'value':value},
        )
    
