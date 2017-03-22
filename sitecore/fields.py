from wagtail.wagtailcore.fields import RichTextField
from sitecore.validators import ValidateShortcodes


class ShortcodeRichTextField(RichTextField):
    def __init__(self, *args, **kwargs):
        if 'validators' in kwargs:
            validators = kwargs.pop('validators')
            if validators:
                validators.append(ValidateShortcodes)
                kwargs['validators'] = validators
        else:
            validators = [ValidateShortcodes]
            kwargs['validators'] = validators

        super(ShortcodeRichTextField, self).__init__(*args, **kwargs)


