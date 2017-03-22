import shortcodes
import html
from django import template
#from django.conf import settings

### create shortcodes

@shortcodes.register("code", "endcode")
def handler(context, content, pargs, kwargs):
    code = html.escape(content)
    return '<code>%s</code>' % (code)

@shortcodes.register("kbd")
def handler(context, content, pargs, kwargs):
    try:
        kbd = html.escape(pargs[0])
    except:
        kbd = "No key specified"
    return '<kbd>%s</kbd>' % (kbd)

parser = shortcodes.Parser(start="[[", end="]]", esc="\\")

### create filter

register = template.Library()

@register.filter('shortcodes')
def shortcodes_filter(value):
    try:
        return parser.parse(value, context=None)
    except shortcodes.InvalidTagError:
        raise shortcodes.InvalidTagError

