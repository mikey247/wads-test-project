"""
Sitecore Wagtail hooks to append/modify default behaviour of the Wagtail system.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join

from wagtail.core.whitelist import attribute_rule, check_url, allow_without_attributes
from wagtail.core import hooks

@hooks.register('construct_whitelister_element_rules')
def whitelister_element_rules():
    """
    On Save Draft/Publish, Wagtail will sanitize the HTML content of various fields/blocks.
    The modified Hallo.js plugin used in the Rich Text Editor, adds additional HTML markup that
    must be permitted in the whitelist.
    """
    return {
        'code': allow_without_attributes,
        'kbd': allow_without_attributes,
        'var': allow_without_attributes,
        'samp': allow_without_attributes,
        'blockquote': attribute_rule({'class': True}),
    }


@hooks.register('insert_editor_js')
def editor_js():
    """
    This hook inserts additional JavaScript into each admin/editor page, using the hallo-custom.js
    file and the additional inline js to register each new plugin.
    """
    js_files = [
    ]
    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>',
        ((settings.STATIC_URL, filename) for filename in js_files)
    )
    return js_includes + format_html(
        """
        <script>
            registerHalloPlugin('superscriptbutton');
            registerHalloPlugin('subscriptbutton');
            registerHalloPlugin('htmlbutton');
        </script>
        """
    )

@hooks.register('insert_global_admin_css')
def global_admin_css():
    """
    This hook inserts additional CSS for the admin/editor page, specifically support for Font Awesome.
    """
    css_files = [
        'sitecore/fontawesome-5.11.2/css/fontawesome.min.css',
    ]
    css_includes = format_html_join(
        '\n', '<link rel="stylesheet" href="{0}">',
        ((static(filename),) for filename in css_files)
    )

    return css_includes
