from wagtailmedia.models import AbstractMedia

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