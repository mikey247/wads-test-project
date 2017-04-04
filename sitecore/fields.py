from wagtail.wagtailcore.fields import RichTextField
from sitecore.parsers import ParseShortcodes


class ShortcodeRichTextField(RichTextField):
    def __init__(self, *args, **kwargs):
        if 'validators' in kwargs:
            validators = kwargs.pop('validators')
            if validators:
                validators.append(ParseShortcodes)
                kwargs['validators'] = validators
        else:
            validators = [ParseShortcodes]
            kwargs['validators'] = validators

        super(ShortcodeRichTextField, self).__init__(*args, **kwargs)


