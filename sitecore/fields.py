"""
Sitecore fields module to implement custom Django/Wagtail fields
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from wagtail.wagtailcore.fields import RichTextField
from sitecore.parsers import ParseShortcodes


class ShortcodeRichTextField(RichTextField):
    """
    Modifies the RichTextField so that the main CharField is also passed through the ParseShortcodes validator.
    Any user embedded shortcodes are checked against the registered codes and exceptions raised as necessary.
    The Wagtail admin interface will display appropriate exceptions on Save Draft or Publish, forcing the author
    to update the content.
    Note: Much check if the validator is already in the list, otherwise EVERY migration adds another entry to the
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


