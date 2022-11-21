"""
Sitecore Wagtail hooks to append/modify default behaviour of the Wagtail system.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join

import wagtail.admin.rich_text.editors.draftail.features as draftail_features

from wagtail.admin.rich_text.converters.html_to_contentstate import BlockElementHandler, InlineStyleElementHandler
from wagtail import hooks

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

@hooks.register('register_rich_text_features')
def register_display_1_feature(features):
    """
    Registering the `display-1` feature, which uses the `h1 class="display-1"` Draft.js block type,
    and is stored as HTML with a `<h1 class="display-1">` tag.
    """
    feature_name = 'display-1'
    type_ = 'display-1'

    control = {
        'type': type_,
        'label': 'D1',
        'description': 'Display Heading 1',
        # Optionally, we can tell Draftail what element to use when displaying those blocks in the editor.
        'element': 'h1',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'h1[class=display-1]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'h1', 'props': {'class': 'display-1'}}}},
    })
    
    #features.default_features.append('display-1')


@hooks.register('register_rich_text_features')
def register_display_2_feature(features):
    """
    Registering the `display-1` feature, which uses the `h1 class="display-1"` Draft.js block type,
    and is stored as HTML with a `<h1 class="display-1">` tag.
    """
    feature_name = 'display-2'
    type_ = 'display-2'

    control = {
        'type': type_,
        'label': 'D2',
        'description': 'Display Heading 2',
        # Optionally, we can tell Draftail what element to use when displaying those blocks in the editor.
        'element': 'h1',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'h1[class=display-2]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'h1', 'props': {'class': 'display-2'}}}},
    })
    
    #features.default_features.append('display-2')

@hooks.register('register_rich_text_features')
def register_display_3_feature(features):
    """
    Registering the `display-3` feature, which uses the `h1 class="display-3"` Draft.js block type,
    and is stored as HTML with a `<h1 class="display-3">` tag.
    """
    feature_name = 'display-3'
    type_ = 'display-3'

    control = {
        'type': type_,
        'label': 'D3',
        'description': 'Display Heading 3',
        # Optionally, we can tell Draftail what element to use when displaying those blocks in the editor.
        'element': 'h1',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'h1[class=display-3]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'h1', 'props': {'class': 'display-3'}}}},
    })
    
    #features.default_features.append('display-3')


@hooks.register('register_rich_text_features')
def register_display_4_feature(features):
    """
    Registering the `display-4` feature, which uses the `h1 class="display-4"` Draft.js block type,
    and is stored as HTML with a `<h1 class="display-4">` tag.
    """
    feature_name = 'display-4'
    type_ = 'display-4'

    control = {
        'type': type_,
        'label': 'D4',
        'description': 'Display Heading 4',
        # Optionally, we can tell Draftail what element to use when displaying those blocks in the editor.
        'element': 'h1',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'h1[class=display-4]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'h1', 'props': {'class': 'display-4'}}}},
    })
    
    #features.default_features.append('display-4')
