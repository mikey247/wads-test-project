import shortcodes
import html
from django import template
import sitecore.config as sitecore_config
from sitecore.parsers import ParseShortcodes

### create shortcodes

@shortcodes.register("code", "/code")
def handler(context, content, pargs, kwargs):
    code = html.escape(content)
    return '<code>%s</code>' % (code)

@shortcodes.register("kbd")
def handler(context, content, pargs, kwargs):
    result = []
    for arg in pargs:
        try:
            kbd = html.escape(arg)
        except:
            kbd = "No key specified"
        result.append('<kbd>%s</kbd>' % (kbd))
    return u' '.join(result)

# create simple_tag (we need context to get parser settings)

parser = shortcodes.Parser(start=sitecore_config.START, end=sitecore_config.END, esc=sitecore_config.ESC)

register = template.Library()

@register.simple_tag()
def shortcodes(value):
    return ParseShortcodes(value)
