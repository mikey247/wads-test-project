from django import forms
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

from sitecore.parsers import ParseShortcodes


class ShortcodeRichTextBlock(blocks.RichTextBlock):

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
    Code highlighting block, using pygments library
    """
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('bash', 'Bash'),
    )

    lang = blocks.ChoiceBlock(choices=LANGUAGE_CHOICES)
    code = blocks.TextBlock(required=True)
    line_nums = blocks.BooleanBlock(required=False, help_text='Check to include line numbers')

    class Meta:
        icon = 'doc-full-inverse'
        

    def render(self, value, context=None):
        src = value['code'].strip('\n')
        lang = value['lang']
        linenos = value['line_nums']

        pyg_lexer = get_lexer_by_name(lang)
        pyg_formatter = get_formatter_by_name('html', linenos=linenos, cssclass='codehilite', style='default', noclasses=False)
        
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


class CoreBlock(blocks.StreamBlock):
    """
    Re-usable core Block for collecting custom streamfield support into one place
    """
    heading = BSHeadingBlock()
    paragraph = ShortcodeRichTextBlock(label='Rich Text Paragraph')
    blockquote = BSBlockquoteBlock()

    image =  ImageChooserBlock()

    email = blocks.EmailBlock()
    code = BSCodeBlock()


    def get_form_context(self, value, prefix='', errors=None):
        context = super(CoreBlock, self).get_form_context(value, prefix=prefix, errors=errors)
        context['block_type'] = 'core-block'
        return context


