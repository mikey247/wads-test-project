# image_formats.py
from django.utils.html import format_html
from wagtail.images.formats import Format, register_image_format


class SiteImageCaptionedFormat(Format):

    def image_to_html(self, image, alt_text, extra_attributes=None):

        default_html = super().image_to_html(image, image.alt_text, extra_attributes)

        return format_html("{}<b><figcaption class='figure-caption'>{}</figcaption></b><i><figcaption class='figure-caption'>{}</figcaption></i>", default_html, image.title, image.caption)


register_image_format(
    SiteImageCaptionedFormat('captioned_fullwidth', 'Captioned', 'figure-img img-fluid rounded', 'width-800')
)
