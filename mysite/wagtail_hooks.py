from django.utils.html import format_html, format_html_join
from django.conf import settings

from wagtail.wagtailcore.whitelist import attribute_rule, check_url, allow_without_attributes
from wagtail.wagtailcore import hooks

@hooks.register('construct_whitelister_element_rules')
def whitelister_element_rules():
    return {
        'code': allow_without_attributes,
        'kbd': allow_without_attributes,
        'var': allow_without_attributes,
        'samp': allow_without_attributes,
        'blockquote': attribute_rule({'class': True}),
    }


@hooks.register('insert_editor_js')
def editor_js():
    js_files = [
        'js/hallo-plugins/hallo-custom.js',
    ]
    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>',
        ((settings.STATIC_URL, filename) for filename in js_files)
    )
    return js_includes + format_html(
        """
        <script>
            registerHalloPlugin('superscriptbutton');
            registerHalloPlugin('subscriptbutton');
            registerHalloPlugin('codebutton');
            registerHalloPlugin('kbdbutton');
            registerHalloPlugin('varbutton');
            registerHalloPlugin('sampbutton');
        </script>
        """
    )

@hooks.register('insert_editor_css')
def editor_css():
    return format_html('<link rel="stylesheet" href="'+settings.STATIC_URL+ 'vendor/font-awesome-4.7.0/css/font-awesome.min.css">')
