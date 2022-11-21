from wagtailmedia.models import AbstractMedia, Media
from wagtailmedia.blocks import AbstractMediaChooserBlock

class SiteMedia(AbstractMedia):
     admin_form_fields =  (
        "title",
        "file",
        "collection",
        "duration",
        "width",
        "height",
        "thumbnail",
        "tags",
    )