from django.core.validators import MinValueValidator, validate_comma_separated_integer_list
from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList, StreamFieldPanel, TabbedInterface
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.models import register_snippet

from sitecore import constants

from .links import LinkBlock
from .text import BSHeadingBlock, BSBlockquoteBlock, CodeBlock



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

    body = blocks.RichTextBlock(
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
        choices=constants.BOOTSTRAP5_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-white',
    )
    
    body_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-light',
    )
    
    link_text_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_TEXT_COLOUR_CHOICES,
        required=False,
        default='text-light',
    )
    
    link_bg_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_BACKGROUND_COLOUR_CHOICES,
        required=False,
        default='bg-primary',
    )

    link_border_colour = blocks.ChoiceBlock(
        choices=constants.BOOTSTRAP5_BORDER_COLOUR_CHOICES,
        required=False,
        default='',
    )


    class Meta:
        template = 'sitecore/blocks/carousel_simple_slide.html'
        icon = 'table'


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
        choices=constants.BOOTSTRAP5_TEXT_COLOUR_CHOICES,
        default='text-dark',
        max_length=128
    )
    
    title_align = models.CharField(
        choices=constants.BOOTSTRAP5_TEXT_ALIGN_CHOICES,
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



class GalleryBlock(blocks.StructBlock):
    GALLERY_FILTERSPEC_CHOICES = [
        ("original", '3 images in a row / original image size'),
        ("fill-300x300", '3 images in a row / 300 x 300 px'),
        ("max-600x600", '3 images in a row / 600 x 600 px'),                        
    ]

    gallery_type = blocks.ChoiceBlock(
        choices = GALLERY_FILTERSPEC_CHOICES,
        help_text = 'Choose Gallery display style',
        label = 'Gallery Style',
    )

    gallery_image_title = blocks.BooleanBlock(
        required=False,
        help_text="Show Image Title",
    )

    gallery_image_caption = blocks.BooleanBlock(
        required=False,
        help_text="Show Image Caption",
    )

    gallery_images = blocks.ListBlock(
        ImageChooserBlock(),
        label='Gallery Images'
    )

    
    class Meta:
        icon = 'image'
        label = 'Gallery'
        template = 'sitecore/blocks/gallery_block.html'



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
        choices=constants.BOOTSTRAP5_TEXT_ALIGN_CHOICES,
        default='text-center',
        max_length=128
    )

    text_colour = models.CharField(
        choices=constants.BOOTSTRAP5_TEXT_COLOUR_CHOICES,
        default='text-light',
        max_length=128
    )
    
    bg_colour = models.CharField(
        choices=constants.BOOTSTRAP5_BACKGROUND_COLOUR_CHOICES,
        default='bg-transparent',
        max_length=128
    )

    border_colour = models.CharField(
        choices=constants.BOOTSTRAP5_BORDER_COLOUR_CHOICES,
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
        choices=constants.BOOTSTRAP5_UNIT_CHOICES,
        default='rem',
        max_length=128
    )
    
    button_colour = models.CharField(
        choices=constants.BOOTSTRAP5_BUTTON_COLOUR_CHOICES,
        default='btn btn-primary',
        max_length=128
    )

    button_size = models.CharField(
        choices=constants.BOOTSTRAP5_BUTTON_SIZE_CHOICES,
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
