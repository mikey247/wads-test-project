from django.utils.functional import cached_property
from django import forms
from wagtail.wagtailcore import blocks
from sitecore.validators import ValidateShortcodes


class ShortcodeRichTextBlock(blocks.RichTextBlock):

    @cached_property
    def field(self):
        from wagtail.wagtailadmin.rich_text import get_rich_text_editor_widget
        return forms.CharField(validators=[ValidateShortcodes],widget=get_rich_text_editor_widget(self.editor), **self.field_options)


