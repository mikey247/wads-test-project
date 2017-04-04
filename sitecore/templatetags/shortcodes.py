import shortcodes
import html
from django import template
from sitecore.parsers import ParseShortcodes

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

# create simple_tag (we need context to get parser settings)

register = template.Library()

@register.simple_tag(takes_context=True)
def shortcodes(context, value):
    return ParseShortcodes(value, context)
