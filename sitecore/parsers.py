"""
Sitecore parser module for implementing embedded shortcodes in user entered rich text fields and blocks, and
the handling of markdown and shortcodes combined for markdown text fields and blocks.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""
import markdown # TODO replace with custom version for Bootstrap3 formatted output
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
    

def ParseMarkdownAndShortcodes(value):
    """
    This is the both the output parser AND validator used in the MarkdownShortcode Block/Field objects. On
    Save Draft/Publish, the content of those fields will be run through this parser to determine if the
    provided content contains valid shortcodes. Invalid shortcodes will raise exceptions in the page render
    process and return a 500 page error. On page render, this parser is used to generate the output HTML,
    and has therefore already been validated.
    Note: Markdown is processed FIRST: this is to process (and remove):
      Links: [text](link)
      Footnote refs: text[^footnote_label] text
      Footnote content: [^footnote_label]: text
    i.e., process any instances of [*] notation which would break Shortcode processing -- assuming [ and ] are
    used as delimiters.
    Note: There is no exception mechanism for the Markdown parse stage.
    """
    md_parser = markdown.Markdown(extensions=['markdown.extensions.tables','markdown.extensions.footnotes'])
    sc_parser = shortcodes.Parser(start=sitecore_config.START, end=sitecore_config.END, esc=sitecore_config.ESC)

    md_text = md_parser.reset().convert(mark_safe(value))

    try:
        return mark_safe(sc_parser.parse(mark_safe(md_text)))
    except shortcodes.InvalidTagError:
        raise ValidationError(
            _('Invalid shortcode tag(s) detected, please correct.'),
            params={'value':md_text},
        )
    except shortcodes.RenderingError as e:
        raise ValidationError(
            _('Invalid shortcode tag(s) detected, please correct. Details: %s' % str(e)),
            params={'value':md_text},
        )
    
