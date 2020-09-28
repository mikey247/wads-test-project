"""
Sitecore blocks module to implement several Wagtail Streamfield blocks for page building
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

# from django import forms
# from django.core.validators import MinValueValidator, validate_comma_separated_integer_list
# from django.db import models
# from django.utils.encoding import force_text
# from django.utils.functional import cached_property
# from django.utils.safestring import mark_safe
# from django.utils.translation import ugettext_lazy as _

# from django_select2.forms import Select2Widget

# from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, StreamFieldPanel, TabbedInterface
# from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks
# from wagtail.core.fields import StreamField, RichTextField
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
# from wagtail.snippets.models import register_snippet

# from pygments import highlight
# from pygments.formatters import get_formatter_by_name
# from pygments.lexers import get_lexer_by_name

# from sitecore import constants
# from sitecore.parsers import ParseMarkdownAndShortcodes, ParseShortcodes

# from taggit.managers import TaggableManager
# from taggit.models import TaggedItemBase

from .links import LinkBlock
from .text import BSCodeBlock, BSHeadingBlock, BSBlockquoteBlock
from .text import MarkdownAndShortcodeTextBlock, TextSnippet
from .embedded import CarouselSnippet, IconCardDeckSnippet
from .section import SubSectionBlock, TabBlock, PillBlock, AccordionBlock
from .section import NestedCoreBlock, TwoColStructValue, TwoColBlock


class SplashBlock(blocks.StreamBlock):
    """
    Re-usable splash Block for collecting standard and streamfield support for Splash Content
    """

    paragraph = blocks.RichTextBlock(
        features=['bold','italic','hr','ol','ul','link','document-link','image','embed',
                  'display-1','display-2','display-3','display-4', 
                  'h1', 'h2', 'h3', 'h4',],
        label='Rich Text Paragraph',
        #validators=[ParseShortcodes],
    )
    image =  ImageChooserBlock(
        template='sitecore/blocks/rendition.html'
    )
    docs = DocumentChooserBlock(
        template='sitecore/blocks/document.html'
    )
    page = blocks.PageChooserBlock(
        required=False,
    )
    carousel = SnippetChooserBlock(
        CarouselSnippet,
        #group='3. Embedded Content',
        template='sitecore/blocks/carousel.html'
    )

    two_cols = TwoColBlock(group='Section Blocks')

    # Override methods

    def get_form_context(self, value, prefix='', errors=None):
        context = super(CoreBlock, self).get_form_context(value, prefix=prefix, errors=errors)
        context['block_type'] = 'splash-block'
        return context

    
    class Meta:
        template = 'sitecore/blocks/splash_streamblock.html'


        
class CoreBlock(blocks.StreamBlock):
    """
    Re-usable core Block for collecting standard and custom streamfield support into one place
    """

    paragraph = blocks.RichTextBlock(
        label='Rich Text Paragraph',
        group='1. Structured Content',
    )
    markdown = MarkdownAndShortcodeTextBlock(
        label='Markdown Paragraph',
        group='1. Structured Content',
    )

    image =  ImageChooserBlock(
        group='2. Linked Content',
        template='sitecore/blocks/rendition.html'
    )
    docs = DocumentChooserBlock(
        group='2. Linked Content',
        template='sitecore/blocks/document.html'
    )
    page = blocks.PageChooserBlock(
        required=False,
        group='2. Linked Content',
    )

    code = BSCodeBlock(
        group='3. Embedded Content',
    )

    carousel = SnippetChooserBlock(
        CarouselSnippet,
        group='3. Embedded Content',
        template='sitecore/blocks/carousel.html'
    )
    icon_card_deck = SnippetChooserBlock(
        IconCardDeckSnippet,
        group='3. Embedded Content',
        template='sitecore/blocks/icon_card_deck.html'
    )

    text_snippet = SnippetChooserBlock(
        TextSnippet,
        group = '3. Embedded Content',
        template='sitecore/tags/text_snippet.html'
        )

    tab = TabBlock(group='Section Blocks')

    pill = PillBlock(group='Section Blocks')

    accordion = AccordionBlock(group='Section Blocks')

    two_cols = TwoColBlock(group='Section Blocks')

    # Override methods

    def get_form_context(self, value, prefix='', errors=None):
        context = super(CoreBlock, self).get_form_context(value, prefix=prefix, errors=errors)
        context['block_type'] = 'core-block'
        return context


    class Meta:
        template = 'sitecore/blocks/core_streamblock.html'
    

