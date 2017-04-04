from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django import forms

from wagtail.wagtailcore import blocks

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name

from sitecore.parsers import ParseShortcodes


class ShortcodeRichTextBlock(blocks.RichTextBlock):

    @cached_property
    def field(self):
        from wagtail.wagtailadmin.rich_text import get_rich_text_editor_widget
        return forms.CharField(validators=[ParseShortcodes],widget=get_rich_text_editor_widget(self.editor), **self.field_options)


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
        icon = 'fa fa-code'
        

    def render(self, value, context=None):
        src = value['code'].strip('\n')
        lang = value['lang']
        linenos = value['line_nums']

        pyg_lexer = get_lexer_by_name(lang)
        pyg_formatter = get_formatter_by_name('html', linenos=False, cssclass='codehilite', style='default', noclasses=False)
        
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
        icon = 'fa fa-quote-left'
        template = 'bootstrapblocks/blockquote.html'
