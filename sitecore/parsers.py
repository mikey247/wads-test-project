"""
Sitecore parser module for implementing embedded shortcodes in user entered rich text fields and blocks, and
the handling of markdown and shortcodes combined for markdown text fields and blocks.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""
import markdown  # TODO replace with custom version for Bootstrap3 formatted output
import shortcodes
import sitecore.config as sitecore_config

from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from wagtail.blocks.stream_block import StreamBlockValidationError


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
    except shortcodes.ShortcodeSyntaxError as e:
        raise ValidationError(
            _('ShortcodeSyntaxError: %s' % str(e)),
            params={'value': value},
        )
    except shortcodes.ShortcodeRenderingError as e:
        raise ValidationError(
            _('ShortcodeRenderingError: %s (%s)' % (str(e), str(e.__cause__))),
            params={'value': value},
        )
    

def ParseMarkdownAndShortcodes(value):
    """
    This is the both the output parser AND validator used in the MarkdownShortcode Block/Field objects. On
    Save Draft/Publish, the content of those fields will be run through this parser to determine if the
    provided content contains valid shortcodes. Invalid shortcodes will raise exceptions in the page render
    process and return a 500 page error. On page render, this parser is used to generate the output HTML,
    and should therefore have already been validated. Note that any errors raised on page render will
    produce an error page on the published page.
    Note: Markdown is processed FIRST: this is to process (and remove):
      Links: [text](link)
      Footnote refs: text[^footnote_label] text
      Footnote content: [^footnote_label]: text
    i.e., process any instances of [*] notation which would break Shortcode processing -- assuming [ and ] are
    used as delimiters.
    Note: There is no exception mechanism for the Markdown parse stage.
    """
    md_parser = markdown.Markdown(extensions=['markdown.extensions.tables', 'markdown.extensions.footnotes'])
    sc_parser = shortcodes.Parser(start=sitecore_config.START, end=sitecore_config.END, esc=sitecore_config.ESC)

    md_text = md_parser.reset().convert(mark_safe(value))

    try:
        return mark_safe(sc_parser.parse(mark_safe(md_text)))
    except shortcodes.ShortcodeSyntaxError as e:
        raise ValidationError(
            _('ShortcodeSyntaxError: %s' % str(e)),
            params={'value': md_text},
        )
    except shortcodes.ShortcodeRenderingError as e:
        raise ValidationError(
            _('ShortcodeRenderingError: %s (%s)' % (str(e), str(e.__cause__))),
            params={'value': md_text},
        )


def ValidateCoreBlocks(value):
    """
    This method is used to address a problem with StreamField and MarkdownAndShortcodeTextBlock validation.

    Issue:
    On Save Draft or Publish, Wagtail is not validating any of the blocks in the StreamField. This means
    the ParseMarkdownAndShortcodes validator/renderer is not called, so errors in shortcodes are not
    detected. However, the parser is correctly called on page render and will raise exceptions if errors
    are found in the block content, leading to a 500 - Internal Server Error

    Solution:
    A validator is attached to the StreamField (of CoreBlocks) and executed on Save Draft/Publish. This
    method only processes 'markdown' blocks in the stream field block list. The content is passed
    directly to the parser, with the exception trapped and passed to the StreamBlockValidationError
    mechanism.

    Notes:
    1) This is not an elegant solution. Non-markdown blocks are not validated, however they do not
    typically raise exceptions that lead to failed page renders.
    2) The data format of the passed value.stream_data CHANGES depending on action of Save Draft or Publish
    2A) The value.stream_data array elements are tuple lists with THREE entries (FOR SAVE DRAFT)
       [0] The block type/name e.g., 'markdown'
       [1] The block value data e.g., the markdown field content
       [2] The Object ID
    2B) The value.stream_data array elements are dict objects with THREE entries (FOR PUBLISH)
       ['type' ] The block type/name e.g., 'markdown'
       ['value'] The block value data e.g., the markdown field content
       ['id']    The Object ID
    3) The value items list is built from [0] or 'value' depending on isinstance type checking

    TO-DO:
    Explore the other members of value, to see if we can retrieve the blocks themselves and access the
    validators they have been assigned, without checking the type/name and calling directly

    See: https://github.com/UoMResearchIT/wagtail-darfur/issues/2
    See: https://github.com/wagtail/wagtail/issues/4122

    Issue:
    In Wagtail 2.12, the stream_data field was deprecated (but still available). This has now been removed
    completely in later releases and the code below failed (noticed in Wagtail 2.15.3)
    
    See: https://docs.wagtail.org/en/stable/releases/2.12.html:
    
    'stream_data on StreamField values is deprecated'

    The stream_data property of StreamValue is commonly used to access
    the underlying data of a StreamField. However, this is
    discouraged, as it is an undocumented internal attribute and has
    different data representations depending on whether the value
    originated from the database or in memory, typically leading to
    errors on preview if this has not been properly accounted for. As
    such, stream_data is now deprecated.

    The recommended alternative is to index the StreamField value
    directly as a list; for example, page.body[0].block_type and
    page.body[0].value instead of page.body.stream_data[0]['type'] and
    page.body.stream_data[0]['value']. This has the advantage that it
    will return the same Python objects as when the StreamField is
    used in template code (such as Page instances for
    PageChooserBlock). However, in most cases, existing code using
    stream_data is written to expect the raw JSON-like representation
    of the data, and for this the new property raw_data (added in
    Wagtail 2.12) can be used as a drop-in replacement for
    stream_data.

    Temporary Solution:
    Swap to raw_data as suggested. The following code addresses the issue of how data is structured
    depending on source i.e., it's a dictionary or list.

    TODO: Replace with code that uses recommendation above and access directly as a list.

    """

    items = [data['value'] if isinstance(data, dict) else data[1] for data in value.raw_data if 'markdown' in (data['type'] if isinstance(data, dict) else data[0])]

    for item in items:
        try:
            ParseMarkdownAndShortcodes(item)
        except ValidationError as err:
            raise StreamBlockValidationError(
                non_block_errors=ValidationError(
                    _('%s' % str(err)),
                    code='invalid',
                    params={'value': str(err)},
                ),
            )
