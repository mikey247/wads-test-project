# Section Block 

# Section Block that is made up of custom snippets that will take up a
# section in a Bootstrap 'Tab' or 'Pills' (in Navs ->
# https://getbootstrap.com/docs/4.5/components/navs/) or 'Accordion'
# (see -> https://getbootstrap.com/docs/4.5/components/collapse/).

# This will allow users to create information dense areas while using
# little space e.g. 'Meet The Team' but instead of being a list of
# team members it can be split into groups in tabs e.g. RI Team, RSE
# Team etc

# from django import forms
# from django.core.validators import MinValueValidator, validate_comma_separated_integer_list
# from django.db import models
# from django.utils.encoding import force_text
# from django.utils.functional import cached_property
# from django.utils.safestring import mark_safe
# from django.utils.translation import ugettext_lazy as _

# from django_select2.forms import Select2Widget

# from wagtail.contrib.table_block.blocks import TableBlock
# from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, StreamFieldPanel, TabbedInterface
from wagtail.core import blocks
# from wagtail.core.fields import StreamField, RichTextField
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
#from wagtail.snippets.models import register_snippet

from sitecore import constants
# from sitecore.parsers import ParseMarkdownAndShortcodes, ParseShortcodes

# from taggit.managers import TaggableManager
# from taggit.models import TaggedItemBase

from .text import MarkdownAndShortcodeTextBlock, CodeBlock
from .text import TextSnippet


class SubSectionBlock(blocks.StructBlock):

    title = blocks.CharBlock()

    content = blocks.RichTextBlock(
        label='Rich Text',
    )
    
    class Meta:
        icon = 'form'
        template = 'sitecore/blocks/subsection_block.html'


class TabBlock(blocks.StructBlock):

    tab_section = blocks.ListBlock(SubSectionBlock(), label='Tab Section(s)')

    class Meta:
        template = 'sitecore/blocks/tab_block.html'
        icon = 'form'


class PillBlock(blocks.StructBlock):

    pill_type_choices = [

        ("PILL", 'Pill'),
        ("PILL-VERT-L",'Vertical Pill (Left Tabs)'),
        ("PILL-VERT-R",'Vertical Pill Right (Right Tabs)'),
  
    ]

    pill_type = blocks.ChoiceBlock(
        choices = pill_type_choices, 
        help_text = 'Choose pill display style',
        label = 'Pill Style',
        default = 'PILL'
        )


    pill_section = blocks.ListBlock(SubSectionBlock(), label='Pill Section(s)')

    class Meta:
        template = 'sitecore/blocks/pill_block.html'
        icon = 'form'


class AccordionBlock(blocks.StructBlock):

    accordion_type_choices = [

        ("ACCORDION", 'Accordion (Default - First tab open)'),
        ("ACCORDION-CLOSED",'Accordion - (All tabs closed)' ),
  
    ]

    accordion_type = blocks.ChoiceBlock(
        choices = accordion_type_choices, 
        help_text = 'Choose Accordion display style',
        label = 'Accordion Style',
        default = 'ACCORDION'
        )

    accordion_section = blocks.ListBlock(SubSectionBlock(), label='Accordion Section(s)')


    class Meta:
        template = 'sitecore/blocks/accordion_block.html'
        icon = 'form'


class NestedCoreBlock(blocks.StreamBlock):
    """
    Re-usable Nested CoreBlock for collecting standard and custom streamfield support into one place
    """

    nested_paragraph = blocks.RichTextBlock(
        label='Rich Text Paragraph',
        group='1. Structured Content',
    )
    
    nested_markdown = MarkdownAndShortcodeTextBlock(
        label='Markdown Paragraph',
        group='1. Structured Content',
    )

    nested_image =  ImageChooserBlock(
        group='2. Linked Content',
        template='sitecore/blocks/rendition.html'
    )
    nested_docs = DocumentChooserBlock(
        group='2. Linked Content',
        template='sitecore/blocks/document.html'
    )
    
    nested_page = blocks.PageChooserBlock(
        required=False,
        group='2. Linked Content',
    )

    nested_code = CodeBlock(
        group='3. Embedded Content',
    )

    nested_text_snippet = SnippetChooserBlock(
        TextSnippet,
        template='tags/text_snippet.html',
        label = 'Text Snippet',
        group='3. Embedded Content',
    )

    # Override methods

    def get_form_context(self, value, prefix='', errors=None):
        context = super(CoreBlock, self).get_form_context(value, prefix=prefix, errors=errors)
        context['block_type'] = 'nested-core-block'
        return context


    class Meta:
        template = 'sitecore/blocks/nested_streamblock.html'


        
class TwoColStructValue(blocks.StructValue):
    """
    Defines a "value_class" for the TwoColBlock class below, which enables a StructBlock to have some control over context in rendering.
    """
    def col_one_layout(self):
        col_ratio = self.get('col_ratio')
        if col_ratio == '1:2':
            return "col-12 col-md-4 ps-md-0 m-0"
        elif col_ratio == '1:3':
            return "col-12 col-md-3 ps-md-0 m-0"
        elif col_ratio == '2:1':
            return "col-12 col-md-8 ps-md-0 m-0"
        elif col_ratio == '3:1':
            return "col-12 col-md-9 ps-md-0 m-0"
        else:
            return "col-12 col-md-6 ps-md-0 m-0"

    def col_two_layout(self):
        col_ratio = self.get('col_ratio')
        if col_ratio == '1:2':
            return "col-12 col-md-8 pe-md-0 m-0"
        elif col_ratio == '1:3':
            return "col-12 col-md-9 pe-md-0 m-0"
        elif col_ratio == '2:1':
            return "col-12 col-md-4 pe-md-0 m-0"
        elif col_ratio == '3:1':
            return "col-12 col-md-3 pe-md-0 m-0"
        else:
            return "col-12 col-md-6 pe-md-0 m-0"
        
        
class TwoColBlock(blocks.StructBlock):

    col_ratio = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_TWOCOL_RATIO_CHOICES,
        default='1:1',
    )

    col_one_content = NestedCoreBlock(label='Column - 1',)
    col_two_content = NestedCoreBlock(label='Column - 2')

    class Meta:
        template = 'sitecore/blocks/twocol_structblock.html'
        icon = 'form'
        label='Two Columns'
        value_class = TwoColStructValue



