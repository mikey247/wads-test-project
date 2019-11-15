"""
Sitecore blocks module to implement several Wagtail Streamfield blocks for page building
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

from django import forms
from django.core.validators import MinValueValidator, validate_comma_separated_integer_list
from django.db import models
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, StreamFieldPanel, TabbedInterface
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.models import register_snippet

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

from sitecore import constants
from sitecore.parsers import ParseMarkdownAndShortcodes, ParseShortcodes


class CSVIntListCharBlock(blocks.FieldBlock):
    """
    Adds the Django forms.CharField WITH the validate_comma_separated_integer_list validator to a StreamField block.
    This enables the BSCodeBlock below to include a field allowing entry of code lines to be highlighted.
    Note: The default blocks.CharBlock does not include any validators nor does it allow them to be passed as arguments.
    """

    def __init__(self, required=True, help_text=None, max_length=None, min_length=None, **kwargs):
        self.field = forms.CharField(
            required=required,
            validators=[validate_comma_separated_integer_list],
            help_text=help_text,
            max_length=max_length,
            min_length=min_length
        )
        super(CSVIntListCharBlock, self).__init__(**kwargs)

    def get_searchable_content(self, value):
        return [force_text(value)]


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
        template = 'bootstrapblocks/richtext_shortcode.html'


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
        return [force_text(value)]

    class Meta:
        icon = "pilcrow"
        template = 'bootstrapblocks/markdown_shortcode.html'


class LinkStructValue(blocks.StructValue):
    """
    Defines a "value_class" for the LinkBlock class below.
    Enables a StructBlock to have some control over context in rendering.
    As Wagtail does not (yet) have the facility to provide a unified link field, we must provide one field per link type.
    The LinkBlock class allows for:
      - internal (page) links
      - download (document) links
      - external (url) links
    This class retrieves all three values and returns the first non-empty field in the order internal,download,external
    """

    def resolve_link(self):
        internal_link = self.get('internal_link')
        download_link = self.get('download_link')
        external_link = self.get('external_link')
        link_title = self.get('link_title')
        short_title = self.get('short_title')

        if internal_link:
            details = {
                'type': 'internal',
                'title': (link_title or internal_link.title),
                'short': (short_title or "Read More"),
                'url': internal_link.url,
                'icon': 'fas fa-chevron-right',
            }
        elif download_link:
            details = {
                'type': 'download',
                'title': (link_title or "Download"),
                'short': (short_title or "Download"),
                'url': download_link.url,
                'icon': 'fas fa-download',
            }
        elif external_link:
            details = {
                'type': 'external',
                'title': (link_title or external_link),
                'short': (short_title or "Read More"),
                'url': external_link,
                'icon': 'fas fa-external-link-alt',
            }
        else:
            details = {
                'type': None,
                'title': None,
                'short': None,
                'url': None,
                'icon': None,
            }

        return details
    

class LinkBlock(blocks.StructBlock):
    internal_link = blocks.PageChooserBlock(
        label=u'Link (Internal Page)',
        required=False,
        help_text=_('Use to link to selected internal page OR...')
    )

    download_link = DocumentChooserBlock(
        label=u'Download (Document)',
        required=False,
        help_text=_('Use to link to selected document for download OR')
    )

    external_link = blocks.URLBlock(
        label=u'Link (External URL)',
        required=False,
        help_text=_('Use to link to an external site.')
    )

    link_title = blocks.CharBlock(
        label=u'Link Title Text',
        required=False,
        help_text=_('Specify title for external link or provide override title for internal/download links.')
    )

    short_title = blocks.CharBlock(
        label=u'Short Title Text',
        required=False,
        help_text=_('Specify short title for use on small screens. Defaults to "Read More" or "Download".')
    )


    class Meta:
        value_class = LinkStructValue
        

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
        context = super(BSHeadingBlock, self).get_form_context(value, prefix=prefix, errors=errors)
        #context['block_type'] = 'bs-heading-block'
        return context


    class Meta:
        icon = 'title'
        template = 'bootstrapblocks/heading.html'
        #form_template = 'bootstrapblocks/admin/heading.html'
        #form_classname = 'heading-block struct-block'


class BSCodeBlock(blocks.StructBlock):
    """
    Code highlighting block in, using pygments library wrapped in Bootstrap 3 markup
    Options include language selection, a comma separated list of integers for lines to be highlighted
    and a toggle for display of all line numbers or not.
    """

    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('bash', 'Bash'),
    )

    lang = blocks.ChoiceBlock(
        choices=LANGUAGE_CHOICES
    )

    code = blocks.TextBlock(
        required=True
    )

    hl_lines = CSVIntListCharBlock(
        required=False
    )

    line_nums = blocks.BooleanBlock(
        required=False,
        help_text=_('Check to include line numbers')
    )

    class Meta:
        icon = 'doc-full-inverse'
        

    def render(self, value, context=None):
        src = value['code'].strip('\n')
        lang = value['lang']
        linenos = value['line_nums']

        pyg_lexer = get_lexer_by_name(lang)
        hl_lines = value['hl_lines'].split(',') if value['hl_lines'] else []
        pyg_formatter = get_formatter_by_name('html', linenos=linenos, hl_lines=hl_lines, cssclass='codehilite', style='default', noclasses=False)
        
        return mark_safe(highlight(src, pyg_lexer, pyg_formatter))


class BSBlockquoteBlock(blocks.StructBlock):
    """
    Block for supporting full Bootstrap 4 <blockquote> markup
    """

    # Blockquote text content
    
    quote = ShortcodeRichTextBlock(
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
        choices=constants.BOOTSTRAP4_TEXT_ALIGN_CHOICES,
        default='text-center',
    )

    quote_text_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-dark',
    )
    
    footer_text_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-secondary',
    )
    
    bg_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP4_BACKGROUND_COLOUR_CHOICES,
        required=False,
        default='bg-light',
    )

    border_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP4_BORDER_COLOUR_CHOICES,
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
        template = 'bootstrapblocks/blockquote.html'


#class CarouselTextBlock(blocks.StreamBlock):
    """
    Block embedded inside each carousel slide - allows subset of main streamfield blocks
    """

    # heading = BSHeadingBlock()
    # paragraph = ShortcodeRichTextBlock(label='Rich Text Paragraph')
    # blockquote = BSBlockquoteBlock()

    # image =  ImageChooserBlock() # perhaps requires carousel specific renderer?
    # docs = DocumentChooserBlock(template='bootstrapblocks/document.html')
    # page = blocks.PageChooserBlock()
    # external = blocks.URLBlock()

    # class Meta:
    #     template = 'bootstrapblocks/carouseltext.html'


#class CarouselSlideBlock(blocks.StructBlock):
    """
    Instance of a carousel item, for holding image reference, caption, detail text and link.
    """

    # title = blocks.CharBlock(required=False)
    # image = ImageChooserBlock() # perhaps requires carousel specific renderer?
    # text = CarouselTextBlock(required=False)


class CarouselSimpleSlideBlock(blocks.StructBlock):
    """
    Default carousel slide.
    Instance of a simple carousel item: background image caption title, caption text, link and background colour/gradient
    """

    # Slide text content (title, text, link)

    title = BSHeadingBlock(
        required=False,
        help_text=_('Main title for the slide (for larger screen sizes)')
    )

    body = MarkdownAndShortcodeTextBlock(
        required=False,
        rows=3
    )

    link = LinkBlock(
        required=False
    )

    # Slide background image content(image, overlay effect)
    
    image = ImageChooserBlock()

    apply_css_effect = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text=_('Check to apply the CSS effect to the image')
    )
    
    css_effect = blocks.CharBlock(
        required=False,
        default='background: linear-gradient(to bottom, rgba(0,0,0,0.0), rgba(0,0,0,0.0) 50%, rgba(0,0,0,0.75) 70%);',
        help_text=_('CSS effect applied to image; default is gradient that darkens towards bottom.')
    )

    # Slide text and button styles

    title_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-white',
    )
    
    body_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-light',
    )
    
    link_text_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-light',
    )
    
    link_bg_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP4_BACKGROUND_COLOUR_CHOICES,
        required=False,
        default='bg-primary',
    )

    link_border_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP4_BORDER_COLOUR_CHOICES,
        required=False,
        default='',
    )


    class Meta:
        template = 'bootstrapblocks/carousel_simple_slide.html'


@register_snippet
class CarouselSnippet(models.Model):
    """
    Instance of an entire carousel slide set. Options are provided for changing the default behaviour. The ListBlock
    allows multiple carousel items to be added as needed.
    """

    # Fields: Section options
    
    title = models.CharField(
        help_text=_('Carousel title - optionally displayed with carousel; used as name in Snippet list'),
        max_length=512
    )

    display_title = models.BooleanField(
        default=False
    )

    title_colour = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        default='text-dark',
        max_length=128
    )
    
    title_align = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_ALIGN_CHOICES,
        default='text-center',
        max_length=128
    )

    # Fields: Carousel display and behaviour options
    
    animate = models.BooleanField(
        help_text=_('Enables carousel animation; automatic unless Ride option is enabled'),
        default=True
    )

    ride = models.BooleanField(
        help_text=_('If carousel animation is enabled, enabling this means user has to interact to start it manually'),
        default=True
    )

    crossfade = models.BooleanField(
        help_text=_('Carousel has fade transition rather than slide when enabled'),
        default=True
    )

    interval = models.IntegerField(
        help_text=_('Delay (in milliseconds) between each slide transition'),
        default=5000
    )

    pause = models.BooleanField(
        help_text=_('Carousel pauses with mouse hover when enabled'),
        default=True
    )

    wrap = models.BooleanField(
        help_text=_('Carousel goes through all slides continuously when enabled; stops at last slide otherwise'),
        default=True
    )

    show_controls = models.BooleanField(
        help_text=_('Carousel includes previous/next controls'),
        default=True
    )

    show_indicators = models.BooleanField(
        help_text=_('Carousel includes slide indicators to show active/num slides and allow direct slide selection'),
        default=True
    )

    # StreamField: Slides
    
    slides = StreamField(
        [
#            ('slide_block', CarouselSlideBlock()),
            ('simple_slide', CarouselSimpleSlideBlock()),
        ],
        null=True,
        blank=True,
    )

    # Wagtail Admin Panels (two pages)
    
    panels = [
        FieldPanel('title'),
        StreamFieldPanel('slides'),
    ]

    style_panels = [
        MultiFieldPanel(
            [
                FieldPanel('display_title'),
                FieldPanel('title_colour'),
                FieldPanel('title_align'),
            ],
            heading='Section Options',),
        MultiFieldPanel(
            [
                FieldPanel('animate'),
                FieldPanel('ride'),
                FieldPanel('crossfade'),
                FieldPanel('interval'),
                FieldPanel('pause'),
                FieldPanel('wrap'),
                FieldPanel('show_controls'),
                FieldPanel('show_indicators'),
            ],
            heading='Carousel Display and Behaviour Options'),
    ]

    # Wagtail Admin: Custom edit_handler for multi-panel admin
    
    edit_handler = TabbedInterface([
        ObjectList(panels, heading="Carousel Slides"),
        ObjectList(style_panels, heading="Style"),
    ])
    

    class Meta:
        verbose_name = 'Carousel Slideshow'

    def __str__(self):
        return self.title



class IconCardStructValue(blocks.StructValue):
    """
    Defines a "value_class" for the IconCardBlock class below, which enables a StructBlock to have some control over context in rendering.
    As Wagtail does not (yet) have the facility to provide a unified link field, we must provide one field per link type.
    The IconCardBlock class allows for internal (page) links and external (url) links to be specified.
    This class retrieves both values and returns the external link if defined, otherwise defaulting to the internal link if it's empty.
    """
    def link(self):
        external_link = self.get('button_external_link')
        internal_link = self.get('button_page_link')
        if external_link:
            return external_link
        elif internal_link:
            return internal_link.url
    
    
class IconCardBlock(blocks.StructBlock):
    """
    Instance of a single "IconCard", used in IconCardDeck snippet model.
    This class defines a number of Wagtail Blocks to build the structured content for a card:
    - CharBlock :: icon - allows user to specify a Font Awesome icon for the head of the card e.g., "fa fa-star"
    - CharBlock :: title - title (e.g., h3) in the card body
    - CharBlock :: text - paragraph text in the card body
    - CharBlock :: button_text - defaults to "Read More" but allows user to change as needed
    - PageChooserBlock :: button_page_link - allows user to link to an internal page with the button
    - URLBlock :: button_external_link - allows user to link to an external url
    The meta value_class uses IconCardStructValue above to provide control over render context and returns one of the
    the two button links as 'link' in the template.
    
    TODO: Pick a better icon.
    """

    icon = blocks.CharBlock(
        required=True,
        default=u'fa fa-star',
        label=u'Icon',
        help_text=_('Card Icon - Specify font awesome library and icon name')
    )

    title = blocks.CharBlock(
        required=True,
        label=u'Card Title',
        help_text=_('Card Title - Presented as a h5 heading')
    )

    text = blocks.CharBlock(
        required=False,
        label=u'Card Main Text',
    )

    button_text = blocks.CharBlock(
        required=False,
        default=u'Read More',
        label=u'Button Text',
    )

    button_page_link = blocks.PageChooserBlock(
        required=False,
        label=u'Button Link (Internal Page)',
        help_text=_('Use button to link to selected internal page OR use external link field below')
    )

    button_external_link = blocks.URLBlock(
        required=False,
        label=u'Button Link (External)',
        help_text=_('Use button to link to external link OR use page link above (but not both)')
    )

    # Column Layout options
    # Specify manually e.g., "col-12 col-sm-6 col-md-3"

    custom_layout = blocks.CharBlock(
        required=True,
        default='col-12 col-sm-12 col-md-4 col-lg-4 col-xl-4',
        label=_('Custom Column Layout'),
        help_text=_('Custom Bootstrap 4 Column layout per card e.g., "col-12 col-sm-4 col-lg-3"'),
    )

    class Meta:
        icon = 'site'
        value_class = IconCardStructValue
        

@register_snippet
class IconCardDeckSnippet(models.Model):
    """
    Instance of "IconCardDeck" snippet model for defining a set of "IconCards" using the IconCardBlock and some styling options.

    - StreamField(IconCardBlock) :: dynamic set of icon card blocks
    - ChoiceBlock :: text-alignment
    - ChoiceBlock :: text-colour
    - ChoiceBlock :: background-colour
    - ChoiceBlock :: border-colour
    - FloatBlock  :: icon-size
    - ChoiceBlock :: icon-size-unit (EM or REM)
    - ChoiceBlock :: button-colour
    - ChoiceBlock :: button-size

    """

    # Card Deck Title and Snippet Instance name
    
    title = models.CharField(
        help_text=_('Icon Card Deck title - optionally displayed with card deck; used as name in Snippet list'),
        max_length=512
    )

    # Card Deck and per-card styling options (for all cards in deck)
    
    text_align = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_ALIGN_CHOICES,
        default='text-center',
        max_length=128
    )

    text_colour = models.CharField(
        choices=constants.BOOTSTRAP4_TEXT_COLOUR_CHOICES,
        default='text-light',
        max_length=128
    )
    
    bg_colour = models.CharField(
        choices=constants.BOOTSTRAP4_BACKGROUND_COLOUR_CHOICES,
        default='bg-transparent',
        max_length=128
    )

    border_colour = models.CharField(
        choices=constants.BOOTSTRAP4_BORDER_COLOUR_CHOICES,
        default='',
        blank=True,
        max_length=128
    )
    
    icon_size = models.FloatField(
        default='9.0',
        max_length=128,
        validators=[MinValueValidator(0.0)]
    )

    icon_size_unit = models.CharField(
        choices=constants.BOOTSTRAP4_UNIT_CHOICES,
        default='rem',
        max_length=128
    )
    
    button_colour = models.CharField(
        choices=constants.BOOTSTRAP4_BUTTON_COLOUR_CHOICES,
        default='btn btn-primary',
        max_length=128
    )

    button_size = models.CharField(
        choices=constants.BOOTSTRAP4_BUTTON_SIZE_CHOICES,
        default='',
        blank=True,
        max_length=128
    )

    display_title = models.BooleanField(
        default=False
    )

    # StreamField for dynamic set of cards from IconCardBlock
    
    cards = StreamField(
        [('icon_card_block', IconCardBlock()),],
    )
    
    # GUI for snippet admin
    
    panels = [
        FieldPanel('title'),
        StreamFieldPanel('cards'),
    ]

    style_panels = [
        MultiFieldPanel(
            [
                FieldPanel('display_title'),
            ],
            heading='Section Options',),
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel('text_align'), FieldPanel('text_colour')]),
                FieldRowPanel([FieldPanel('bg_colour'),FieldPanel('border_colour')]),
                FieldRowPanel([FieldPanel('icon_size'),FieldPanel('icon_size_unit')]),
                FieldRowPanel([FieldPanel('button_colour'),FieldPanel('button_size')]),
            ],
            heading='Card Deck Options',),
    ]
    
    edit_handler = TabbedInterface([
        ObjectList(panels, heading="Cards"),
        ObjectList(style_panels, heading="Style"),
    ])
    
    class Meta:
        verbose_name = u'Icon Card Deck'

    def __str__(self):
        return self.title
 

# class BSTwoColumnBlock(blocks.StructBlock):
#     """
#     Block for holding two Bootstrap 4 columns as a container
#     """
#     pass



# class ContainerBlock(blocks.StreamBlock):
#     """
#     Single level streamblock of non-recursive blocks.
#     Available to container blocks defined below
#     """

#     heading = BSHeadingBlock()
#     markdown = MarkdownAndShortcodeTextBlock(label='Markdown Paragraph')
#     paragraph = ShortcodeRichTextBlock(label='Rich Text Paragraph')
#     blockquote = BSBlockquoteBlock()

#     image =  ImageChooserBlock()
#     #image =  ImageChooserBlock(template='image.html')
#     docs = DocumentChooserBlock(template='bootstrapblocks/document.html')
#     page = blocks.PageChooserBlock(required=False)
#     external = blocks.URLBlock(required=False)

#     email = blocks.EmailBlock()
#     code = BSCodeBlock()


# class BSJumbotronContainerBlock(blocks.StreamBlock):
#     """
#     Holds ContainerBlock stream within a Bootstrap 4 <jumbotron> container
#     """

#     # StreamField for non-recursive dynamic content
    
#     content = StreamField(
#         [('container_block', ContainerBlock()),],
#     )
    

    
    
class CoreBlock(blocks.StreamBlock):
    """
    Re-usable core Block for collecting standard and custom streamfield support into one place
    """

    heading = BSHeadingBlock()
    markdown = MarkdownAndShortcodeTextBlock(label='Markdown Paragraph')
    paragraph = ShortcodeRichTextBlock(label='Rich Text Paragraph', validators=[ParseShortcodes])
    blockquote = BSBlockquoteBlock()

    image =  ImageChooserBlock()
    #image =  ImageChooserBlock(template='image.html')
    docs = DocumentChooserBlock(template='bootstrapblocks/document.html')
    page = blocks.PageChooserBlock(required=False)
    external = blocks.URLBlock(required=False)

    email = blocks.EmailBlock()
    code = BSCodeBlock()
    table = TableBlock(template='bootstrapblocks/table.html')

#    jumbotron = BSJumbotronContainerBlock()
    carousel = SnippetChooserBlock(CarouselSnippet, template='bootstrapblocks/carousel.html')
    icon_card_deck = SnippetChooserBlock(IconCardDeckSnippet, template='bootstrapblocks/icon_card_deck.html')

    def get_form_context(self, value, prefix='', errors=None):
        context = super(CoreBlock, self).get_form_context(value, prefix=prefix, errors=errors)
        context['block_type'] = 'core-block'
        return context
