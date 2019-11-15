"""
Sitecore fields module to implement custom Django/Wagtail fields
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""
from django.forms import CharField
from wagtail.core.fields import RichTextField
from sitecore.parsers import ParseMarkdownAndShortcodes, ParseShortcodes


class ShortcodeRichTextField(RichTextField):
    """
    Modifies the RichTextField so that the main CharField is also passed through the ParseShortcodes validator.
    Any user embedded shortcodes are checked against the registered codes and exceptions raised as necessary.
    The Wagtail admin interface will display appropriate exceptions on Save Draft or Publish, forcing the author
    to update the content.
    Note: Must check if the validator is already in the list, otherwise EVERY migration adds another entry to the
    list of validators.
    """
    def __init__(self, *args, **kwargs):
        if 'validators' in kwargs:
            validators = kwargs.pop('validators')
            if validators:
                if not ParseShortcodes in validators:
                    validators.append(ParseShortcodes)
                kwargs['validators'] = validators
        else:
            validators = [ParseShortcodes]
            kwargs['validators'] = validators

        super(ShortcodeRichTextField, self).__init__(*args, **kwargs)


    class Meta:
        template = 'bootstrapblocks/richtext_shortcode.html'


class MarkdownShortcodeCharField(CharField):
    """
    Augments the CharField so that the content is also passed through the ParseMarkdownAndShortcodes validator.
    Any user embedded markdown will be processed first, using the default markdown rules and any enabled extensions.
    This should remove any markdown notation containing the shortcode delimiters (see config.py but usually [ and ]).
    Any user embedded shortcodes are checked against the registered codes and exceptions raised as necessary.
    The Wagtail admin interface will display appropriate exceptions on Save Draft or Publish, forcing the author
    to update the content.
    Note: Must check if the validator is already in the list, otherwise EVERY migration adds another entry to the
    list of validators.
    """
    def __init__(self, *args, **kwargs):
        if 'validators' in kwargs:
            validators = kwargs.pop('validators')
            if validators:
                if not ParseMarkdownAndShortcodes in validators:
                    validators.append(ParseMarkdownAndShortcodes)
                kwargs['validators'] = validators
        else:
            validators = [ParseMarkdownAndShortcodes]
            kwargs['validators'] = validators

        super(MarkdownShortcodeCharField, self).__init__(*args, **kwargs)


