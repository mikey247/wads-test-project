"""
Sitecore blocks module to implement several Wagtail Streamfield blocks for page building
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django import forms
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsnippets.blocks import SnippetChooserBlock
from wagtail.wagtailsnippets.models import register_snippet

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

from sitecore.parsers import ParseShortcodes


class CSVIntListCharBlock(blocks.FieldBlock):
    """
    Adds the Django forms.CharField WITH the validate_comma_separated_integer_list validator to a StreamField block.
    This enables the BSCodeBlock below to include a field allowing entry of code lines to be highlighted.
    Note: The default blocks.CharBlock does not include any validators nor does it allow them to be passed as arguments.
    """

    def __init__(self, required=True, help_text=None, max_length=None, min_length=None, **kwargs):
        self.field = forms.CharField(
            required=required,
            validators=[validate_comma_separated_integer_list],
            help_text=help_text,
            max_length=max_length,
            min_length=min_length
        )
        super(CSVIntListCharBlock, self).__init__(**kwargs)

    def get_searchable_content(self, value):
        return [force_text(value)]


class ShortcodeRichTextBlock(blocks.RichTextBlock):
    """
    Modifies the RichTextBlock so that the main CharField is also passed through the ParseShortcodes validator.
    Any user embedded shortcodes are checked against the registered codes and exceptions raised as necessary.
    The Wagtail admin interface will display appropriate exceptions on Save Draft or Publish, forcing the author
    to update the content.
    """
    
    @cached_property
    def field(self):
        from wagtail.wagtailadmin.rich_text import get_rich_text_editor_widget
        return forms.CharField(validators=[ParseShortcodes],widget=get_rich_text_editor_widget(self.editor), **self.field_options)

        
    class Meta:
        icon = 'pilcrow'


class BSHeadingBlock(blocks.StructBlock):
    """
    Heading block with selection of h2-6 and optional sub-heading in <small>
    """

    HEADINGS = (
        ('h2', 'h2'),
        ('h3', 'h3'),
        ('h4', 'h4'),
        ('h5', 'h5'),
        ('h6', 'h6'),
    )

    level = blocks.ChoiceBlock(widget=forms.RadioSelect, required=True, choices=HEADINGS)
    title = blocks.CharBlock(required=True)
    sub_title = blocks.CharBlock(required=False, help_text=_('Optional sub-heading in small text'))

    def get_form_context(self, value, prefix='', errors=None):
        context = super(BSHeadingBlock, self).get_form_context(value, prefix=prefix, errors=errors)
        #context['block_type'] = 'bs-heading-block'
        return context


    class Meta:
        icon = 'title'
        template = 'bootstrapblocks/heading.html'
        form_template = 'bootstrapblocks/admin/heading.html'
        form_classname = 'heading-block struct-block'


class BSCodeBlock(blocks.StructBlock):
    """
    Code highlighting block in, using pygments library wrapped in Bootstrap 3 markup
    Options include language selection, a comma separated list of integers for lines to be highlighted
    and a toggle for display of all line numbers or not.
    """

    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('bash', 'Bash'),
    )

    lang = blocks.ChoiceBlock(choices=LANGUAGE_CHOICES)
    code = blocks.TextBlock(required=True)
    hl_lines = CSVIntListCharBlock(required=False)
    line_nums = blocks.BooleanBlock(required=False, help_text='Check to include line numbers')

    class Meta:
        icon = 'doc-full-inverse'
        

    def render(self, value, context=None):
        src = value['code'].strip('\n')
        lang = value['lang']
        linenos = value['line_nums']

        pyg_lexer = get_lexer_by_name(lang)
        hl_lines = value['hl_lines'].split(',') if value['hl_lines'] else []
        pyg_formatter = get_formatter_by_name('html', linenos=linenos, hl_lines=hl_lines, cssclass='codehilite', style='default', noclasses=False)
        
        return mark_safe(highlight(src, pyg_lexer, pyg_formatter))


class BSBlockquoteBlock(blocks.StructBlock):
    """
    Block for supporting full Bootstrap 3 <blockquote> markup
    """

    quote = ShortcodeRichTextBlock(required=True)
    footer = blocks.CharBlock(required=False)
    cite = blocks.CharBlock(required=False)
    reverse = blocks.BooleanBlock(required=False, help_text='Check to right-align the quote')

    class Meta:
        icon = 'openquote'
        template = 'bootstrapblocks/blockquote.html'


class CarouselSlideBlock(blocks.StructBlock):
    """
    Instance of a carousel item, for holding image reference, caption, detail text and link.
    """

    title = blocks.CharBlock(required=False)
    image = ImageChooserBlock() # perhaps requires carousel specific renderer?
    text = blocks.CharBlock(required=False)
    link_page = blocks.PageChooserBlock(required=False)
    link_doc = DocumentChooserBlock(required=False, template='bootstrapblocks/document.html')
    link_external = blocks.URLBlock(required=False)


@register_snippet
class CarouselSnippet(models.Model):
    """
    Instance of an entire carousel slide set. Options are provided for changing the default behaviour. The ListBlock
    allows multiple carousel items to be added as needed.
    """

    title = models.CharField(help_text='Carousel title - optionally displayed with carousel; used as name in Snippet list', max_length=512)

    animate = models.BooleanField(help_text='Carousel has sliding animation effect when enabled', default=True)
    interval = models.IntegerField(help_text='Delay (in milliseconds) between each slide transition', default=5000)
    pause = models.BooleanField(help_text='Carousel pauses with mouse hover when enabled', default=True)
    wrap = models.BooleanField(help_text='Carousel goes through all slides continuously when enabled; stops at last slide otherwise', default=True)

    slides = StreamField([
        ('slide_block', CarouselSlideBlock()),],
        null=True,
        blank=True,
    )

    panels = [
        FieldPanel('title'),
        MultiFieldPanel([
            FieldPanel('animate'),
            FieldPanel('interval'),
            FieldPanel('pause'),
            FieldPanel('wrap'),
        ],
        heading='Carousel Options',
        classname="collapsible collapsed"),
        StreamFieldPanel('slides')
    ]

    
    class Meta:
        verbose_name = 'Carousel Slideshow'

    def __str__(self):
        return self.title


class CoreBlock(blocks.StreamBlock):
    """
    Re-usable core Block for collecting standard and custom streamfield support into one place
    """

    heading = BSHeadingBlock()
    paragraph = ShortcodeRichTextBlock(label='Rich Text Paragraph')
    blockquote = BSBlockquoteBlock()

    image =  ImageChooserBlock()
    #image =  ImageChooserBlock(template='image.html')
    docs = DocumentChooserBlock(template='bootstrapblocks/document.html')

    email = blocks.EmailBlock()
    code = BSCodeBlock()
    table = TableBlock(template='bootstrapblocks/table.html')

    carousel = SnippetChooserBlock(CarouselSnippet, template='bootstrapblocks/carousel.html')

    def get_form_context(self, value, prefix='', errors=None):
        context = super(CoreBlock, self).get_form_context(value, prefix=prefix, errors=errors)
        context['block_type'] = 'core-block'
        return context


