import re

from django import template
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch
from django.utils.functional import cached_property

from wagtail.images.models import Filter
from wagtail.images.shortcuts import get_rendition_or_not_found
from wagtail.images.views.serve import generate_image_url


register = template.Library()
allowed_filter_pattern = re.compile(r"^[A-Za-z0-9_\-\.]+$")


@register.tag(name="rendition")
def rendition(parser, token):
    '''
    Provide custom Django templatetag to handle image renditions that pass a
    template variable holding the filterspec, rather than as an inline piece
    of text.

    This replaces the "image" templatetag with hardcoded filterspecs e.g.,
    "{% image self.article_image fill-1200x300 as photo %}"

    with "rendition" e.g., 
    {% rendition self.article_image self.article_image_filterspec as photo %}

    Wagtail is trying to be clever and improve performance as they want
    it to focus on content. The assumption is that hard-coded filterspecs are
    acceptable. However, there has to be some options for editors when
    controlling styling and layout.

    ----

    Code is taken from core wagtail.image templatetags.

    Basically, parse the templatetag, get the various bits, match to a stored
    image, obtain (or pass) the filterspec and optionally return as a named
    variable for further use in the template (the "as photo" part).

    Once done and all okay, return a RenditionNode using bits.

    '''
    bits = token.split_contents()[1:]
    image_expr = parser.compile_filter(bits[0])
    filter_specs_expr = parser.compile_filter(bits[1])
    bits = bits[2:]

    filter_specs = []
    attrs = {}
    output_var_name = None

    as_context = False  # if True, the next bit to be read is the output variable name
    is_valid = True

    for bit in bits:
        if bit == 'as':
            # token is of the form {% image self.photo max-320x200 as img %}
            as_context = True
        elif as_context:
            if output_var_name is None:
                output_var_name = bit
            else:
                # more than one item exists after 'as' - reject as invalid
                is_valid = False
        else:
            try:
                name, value = bit.split('=')
                attrs[name] = parser.compile_filter(value)  # setup to resolve context variables as value
            except ValueError:
                raise template.TemplateSyntaxError(
                    "attr=value in 'image' tag badly formed (missing =). "
                    "(given argument: {})".format(bit)
                )

    if as_context and output_var_name is None:
        # context was introduced but no variable given ...
        is_valid = False

    if output_var_name and attrs:
        # attributes are not valid when using the 'as img' form of the tag
        is_valid = False

    #if len(filter_specs) == 0:
    if not filter_specs_expr:
        # there must always be at least one filter spec provided
        is_valid = False

    if len(bits) == 0:
        # no resize rule provided eg. {% image page.image %}
        raise template.TemplateSyntaxError(
            "no resize rule provided. "
            "'image' tag should be of the form {% image self.photo max-320x200 [ custom-attr=\"value\" ... ] %} "
            "or {% image self.photo max-320x200 as img %}"
        )

    if is_valid:
        return RenditionNode(image_expr, filter_specs_expr, attrs=attrs, output_var_name=output_var_name)
        #return RenditionNode(image_expr, '|'.join(filter_specs), attrs=attrs, output_var_name=output_var_name)
    else:
        raise template.TemplateSyntaxError(
            "'image' tag should be of the form {% image self.photo max-320x200 [ custom-attr=\"value\" ... ] %} "
            "or {% image self.photo max-320x200 as img %}"
        )


class RenditionNode(template.Node):
    '''
    Get the image and filter based on filter_spec_expr (variable containing filter_spec
    Then return a rendition based on that combination of (image,filter)
    '''
    def __init__(self, image_expr, filter_specs_expr, output_var_name=None, attrs={}):
        self.image_expr = image_expr
        self.output_var_name = output_var_name
        self.attrs = attrs
        self.filter_specs_expr = filter_specs_expr
        self.filter_spec = None

    # LML: Can't used @cached_property as when filter_spec passed as a Variable rather than
    # a string, it's not cached correctly. The last saved filter_spec gets "baked in"
    # when a deployment server instance is restarted, so changes to a specific page'saved
    # article_image_filterspec just doesn't work on Preview OR Publish.

    # LML: Possible that "self.filter_spec = self.filter_specs_expr.resolve(context)" is not
    # resolving to the string, but a step short. Need to investigate further.
    
    @property
    def filter(self):
        return Filter(spec=self.filter_spec)

    def render(self, context):
        try:
            image = self.image_expr.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        if not image:
            return ''

        if not hasattr(image, 'get_rendition'):
            raise ValueError("image tag expected an Image object, got %r" % image)

        try:
            self.filter_spec = self.filter_specs_expr.resolve(context)
        except template.VariableDoesNotExist:
            raise ValueError("rendition tag expected a Filter Object, got %r" % self.filter_specs_expr)

        rendition = get_rendition_or_not_found(image, self.filter)

        if self.output_var_name:
            # return the rendition object in the given variable
            context[self.output_var_name] = rendition
            return ''
        else:
            # render the rendition's image tag now
            resolved_attrs = {}
            for key in self.attrs:
                resolved_attrs[key] = self.attrs[key].resolve(context)
            return rendition.img_tag(resolved_attrs)
