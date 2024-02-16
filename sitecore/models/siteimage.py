from django.db import models

from wagtail.images.models import Image, AbstractImage, AbstractRendition
from wagtail.search import index

class SiteImage(AbstractImage):
    # Add any extra fields to image here

    # eg. To add a caption field:
    alt_text = models.CharField(
        max_length=1024,
        blank=False,
        verbose_name = 'Alt Text (for accessibility)' ,
        help_text='Alt text for accessibility purposes. Be as descriptive as possible.',
        )
    
    caption = models.CharField(
        max_length=1024, 
        blank=True,
        help_text='Caption for photo credits or extra information.',
        )

    admin_form_fields = Image.admin_form_fields + (
        # Then add the field names here to make them appear in the form:
        'alt_text',
        'caption',
    )

    search_fields = AbstractImage.search_fields + [
        index.SearchField('title'),
        index.SearchField('caption'),
        index.SearchField('alt_text'),
    ]
    

class SiteRendition(AbstractRendition):
    image = models.ForeignKey(SiteImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )

