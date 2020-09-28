from django.utils.translation import ugettext_lazy as _

from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


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
