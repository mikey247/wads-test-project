"""
Sitecore blocks module to implement several Wagtail Streamfield blocks for page building
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django import forms
from django.core.validators import MinValueValidator, validate_comma_separated_integer_list
from django.db import models
from django.forms import Media
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet

from django_select2.forms import Select2Widget

from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from sitecore import constants
from sitecore.parsers import ParseMarkdownAndShortcodes, ParseShortcodes

from .code_block_settings import get_language_choices, get_theme, get_prism_version


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

    level = blocks.ChoiceBlock(
        widget=forms.RadioSelect,
        required=True,
        default='h3',
        choices=HEADINGS
    )

    title = blocks.CharBlock(
        required=False
    )

    sub_title = blocks.CharBlock(
        required=False,
        help_text=_('Optional sub-heading in small text')
    )

    def get_form_context(self, value, prefix='', errors=None):
        context = super().get_form_context(value, prefix=prefix, errors=errors)
        #context['block_type'] = 'bs-heading-block'
        return context


    class Meta:
        icon = 'title'
        template = 'sitecore/blocks/heading.html'
        #form_template = 'sitecore/admin/blocks/heading.html'
        #form_classname = 'heading-block struct-block'


class BSBlockquoteBlock(blocks.StructBlock):
    """
    Block for supporting full Bootstrap 4 <blockquote> markup
    """

    # Blockquote text content
    
    quote = blocks.RichTextBlock(
        required=True
    )

    footer = blocks.CharBlock(
        required=False
    )

    cite = blocks.CharBlock(
        required=False
    )

    # Blockquote display options
    
    quote_align = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_TEXT_ALIGN_CHOICES,
        default='text-center',
    )

    quote_text_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-dark',
    )
    
    footer_text_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-secondary',
    )
    
    bg_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_BACKGROUND_COLOUR_CHOICES,
        required=False,
        default='bg-light',
    )

    border_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_BORDER_COLOUR_CHOICES,
        default='',
        required=False,
    )

    jumbotron_wrapper = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text=_('Check to wrap quote in jumbotron/hero-unit')
    )
    
    class Meta:
        icon = 'openquote'
        template = 'sitecore/blocks/blockquote.html'



class Select2ChoiceBlock(blocks.FieldBlock):
    """
    Modifies the ChoiceBlock to specify use of the Select2Widget, to provide autocomplete for
    overly 'long' choice lists
    """
    
    choices = ()

    def __init__(self, choices=None, default=None, required=True, help_text=None, validators=(), **kwargs):
        if choices is None:
            # no choices specified, so pick up the choice defined at the class level
            choices = self.choices

        if callable(choices):
            # Support of callable choices. Wrap the callable in an iterator so that we can
            # handle this consistently with ordinary choice lists;
            # however, the `choices` constructor kwarg as reported by deconstruct() should
            # remain as the callable
            choices_for_constructor = choices
            choices = CallableChoiceIterator(choices)
        else:
            # Cast as a list
            choices_for_constructor = choices = list(choices)

        # keep a copy of all kwargs (including our normalised choices list) for deconstruct()
        self._constructor_kwargs = kwargs.copy()
        self._constructor_kwargs['choices'] = choices_for_constructor
        if required is not True:
            self._constructor_kwargs['required'] = required
        if help_text is not None:
            self._constructor_kwargs['help_text'] = help_text

        # We will need to modify the choices list to insert a blank option, if there isn't
        # one already. We have to do this at render time in the case of callable choices - so rather
        # than having separate code paths for static vs dynamic lists, we'll _always_ pass a callable
        # to ChoiceField to perform this step at render time.

        # If we have a default choice and the field is required, we don't need to add a blank option.
        callable_choices = self.get_callable_choices(choices, blank_choice=not(default and required))

        self.field = forms.ChoiceField(
            choices=callable_choices,
            required=required,
            help_text=help_text,
            validators=validators,
            widget=Select2Widget,
        )
        super().__init__(default=default, **kwargs)

    def get_callable_choices(self, choices, blank_choice=True):
        """
        Return a callable that we can pass into `forms.ChoiceField`, which will provide the
        choices list with the addition of a blank choice (if blank_choice=True and one does not
        already exist).
        """
        def choices_callable():
            # Variable choices could be an instance of CallableChoiceIterator, which may be wrapping
            # something we don't want to evaluate multiple times (e.g. a database query). Cast as a
            # list now to prevent it getting evaluated twice (once while searching for a blank choice,
            # once while rendering the final ChoiceField).
            local_choices = list(choices)

            # If blank_choice=False has been specified, return the choices list as is
            if not blank_choice:
                return local_choices

            # Else: if choices does not already contain a blank option, insert one
            # (to match Django's own behaviour for modelfields:
            # https://github.com/django/django/blob/1.7.5/django/db/models/fields/__init__.py#L732-744)
            has_blank_choice = False
            for v1, v2 in local_choices:
                if isinstance(v2, (list, tuple)):
                    # this is a named group, and v2 is the value list
                    has_blank_choice = any([value in ('', None) for value, label in v2])
                    if has_blank_choice:
                        break
                else:
                    # this is an individual choice; v1 is the value
                    if v1 in ('', None):
                        has_blank_choice = True
                        break

            if not has_blank_choice:
                return BLANK_CHOICE_DASH + local_choices

            return local_choices
        return choices_callable

    def deconstruct(self):
        """
        Always deconstruct Select2ChoiceBlock instances as if they were plain Select2ChoiceBlocks with their
        choice list passed in the constructor, even if they are actually subclasses. This allows
        users to define subclasses of Select2ChoiceBlock in their models.py, with specific choice lists
        passed in, without references to those classes ending up frozen into migrations.
        """
        return ('sitecore.blocks.Select2ChoiceBlock', [], self._constructor_kwargs)

    def get_searchable_content(self, value):
        # Return the display value as the searchable value
        text_value = force_str(value)
        for k, v in self.field.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2 or text_value == force_str(k2):
                        return [force_str(k), force_str(v2)]
            else:
                if value == k or text_value == force_str(k):
                    return [force_str(v)]
        return []  # Value was not found in the list of choices

    class Meta:
        # No icon specified here, because that depends on the purpose that the
        # block is being used for. Feel encouraged to specify an icon in your
        # descendant block type
        icon = "placeholder"


    
class ShortcodeRichTextBlock(blocks.RichTextBlock):
    """
    Modifies the RichTextBlock so that the main CharField is also passed through the ParseShortcodes validator.
    Any user embedded shortcodes are checked against the registered codes and exceptions raised as necessary.
    The Wagtail admin interface will display appropriate exceptions on Save Draft or Publish, forcing the author
    to update the content.
    """
    
    @cached_property
    def field(self):
        from wagtail.admin.rich_text import get_rich_text_editor_widget

        return forms.CharField(
            widget=get_rich_text_editor_widget(self.editor),
            **self.field_options
        )

        
    class Meta:
        icon = 'pilcrow'
        template = 'sitecore/blocks/richtext_shortcode.html'


class MarkdownAndShortcodeTextBlock(blocks.FieldBlock):
    """
    Modifies the FieldBlock so that the main CharField is also passed through the ParseMarkdownAndShortcodes validator.
    Any user embedded markdown will be processed first, using the default markdown rules and any enabled extensions.
    This should remove any markdown notation containing the shortcode delimiters (see config.py but usually [ and ]).
    Any user embedded shortcodes are checked against the registered codes and exceptions raised as necessary.
    The Wagtail admin interface will display appropriate exceptions on Save Draft or Publish, forcing the author
    to update the content.
    """

    def __init__(
            self,
            required=True,
            help_text=None,
            rows=1,
            max_length=None,
            min_length=None,
            validators=[ParseMarkdownAndShortcodes],
            **kwargs):

        self.field_options = {
            'required': required,
            'help_text': help_text,
            'max_length': max_length,
            'min_length': min_length,
            'validators': validators,
        }
        self.rows = rows
        super().__init__(**kwargs)

    @cached_property
    def field(self):
        from wagtail.admin.widgets import AdminAutoHeightTextInput
        field_kwargs = {'widget': AdminAutoHeightTextInput(attrs={'rows': self.rows})}
        field_kwargs.update(self.field_options)
        return forms.CharField(**field_kwargs)

    def get_searchable_content(self, value):
        return [force_str(value)]

    class Meta:
        icon = "pilcrow"
        template = 'sitecore/blocks/markdown_shortcode.html'


class TextSnippetTag(TaggedItemBase):
    content_object = models.ForeignKey(
        'TextSnippet',
        on_delete=models.CASCADE,
        related_name='tagged_text_snippet'
    )

@register_snippet
class TextSnippet(models.Model):

    title = models.CharField(
        max_length=4096,
        verbose_name="Text Snippet Title",
        )
    
    text = RichTextField()

    tags = TaggableManager(through=TextSnippetTag, blank=True,)

    panels = [
        FieldPanel('title'),
        FieldPanel('tags'),
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.title



class CodeBlock(blocks.StructBlock):
    """
    A Wagtail StreamField block for code syntax highlighting using PrismJS.
    """

    def __init__(self, local_blocks=None, **kwargs):
        # Languages included in PrismJS core
        # Review: https://github.com/PrismJS/prism/blob/gh-pages/prism.js#L602
        self.INCLUDED_LANGUAGES = (
            ('html', 'HTML'),
            ('mathml', 'MathML'),
            ('svg', 'SVG'),
            ('xml', 'XML'),
        )

        if local_blocks is None:
            local_blocks = []
        else:
            local_blocks = local_blocks.copy()

        language_choices, language_default = self.get_language_choice_list(**kwargs)

        local_blocks.extend([
            ('language', blocks.ChoiceBlock(
                choices=language_choices,
                help_text=_('Coding language'),
                label=_('Language'),
                default=language_default,
                identifier='language',
            )),
            ('code', blocks.TextBlock(label=_('Code'), identifier='code')),
        ])

        super().__init__(local_blocks, **kwargs)

    def get_language_choice_list(self, **kwargs):
        # Get default languages
        WCB_LANGUAGES = get_language_choices()
        # If a language is passed in as part of a code block, use it.
        language = kwargs.get('language', False)

        total_language_choices = WCB_LANGUAGES + self.INCLUDED_LANGUAGES

        if language in [lang[0] for lang in total_language_choices]:
            for language_choice in total_language_choices:
                if language_choice[0] == language:
                    language_choices = (language_choice,)
                    language_default = language_choice[0]
        else:
            language_choices = WCB_LANGUAGES
            language_default = None

        return language_choices, language_default

    @property
    def media(self):

        PRISM_VERSION = get_prism_version()
        THEME = get_theme()
        
        if THEME:
            prism_theme = "-{theme}".format(theme=THEME)
        else:
            prism_theme = ""

        js_list = [
            "//cdnjs.cloudflare.com/ajax/libs/prism/{prism_version}/prism.min.js".format(
                prism_version=PRISM_VERSION,
            ),
        ]
       
        # Get the languages for the site from Django's settings, or the default in get_language_choices()
        for lang_code, lang_name in get_language_choices():
            if lang_code not in [included_language[0] for included_language in self.INCLUDED_LANGUAGES]:
                js_list.append(
                    "//cdnjs.cloudflare.com/ajax/libs/prism/{prism_version}/components/prism-{lang_code}.min.js".format(
                        prism_version=PRISM_VERSION,
                        lang_code=lang_code,
                    )
                )
        return Media(
            js=js_list,
            css={
                'all': [
                    "//cdnjs.cloudflare.com/ajax/libs/prism/{prism_version}/themes/prism{prism_theme}.min.css".format(
                        prism_version=PRISM_VERSION,
                        prism_theme=prism_theme,
                    ),
                    "sitecore/wagtailcodeblock/css/wagtail-code-block.min.css",
                ]
            }
        )

    class Meta:
        icon = 'code'
        template = 'sitecore/blocks/code_block.html'
        form_template = 'sitecore/blocks/code_block_form.html'
        form_classname = 'code-block struct-block'
