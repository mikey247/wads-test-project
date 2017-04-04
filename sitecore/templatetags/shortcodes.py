import shortcodes
import html
from django import template
import sitecore.config as sitecore_config
from sitecore.parsers import ParseShortcodes

### create shortcodes

@shortcodes.register("code", "/code")
def handler(context, content, pargs, kwargs):
    content_html = html.escape(content)
    return '<code>%s</code>' % (content_html)

@shortcodes.register("samp", "/samp")
def handler(context, content, pargs, kwargs):
    content_html = html.escape(content)
    return '<samp>%s</samp>' % (content_html)

@shortcodes.register("var", "/var")
def handler(context, content, pargs, kwargs):
    content_html = html.escape(content)
    return '<var>%s</var>' % (content_html)

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

@shortcodes.register("abbr")
def handler(context, content, pargs, kwargs):
    try:
        title = html.escape(pargs[0])
        abbr = html.escape(pargs[1])
    except:
        title = "Invalid abbreviation"
        
    return '<abbr title="%s">%s</abbr>' % (title,abbr)


# create simple_tag (cleaner processing as we can mark_safe in code rather than a filter chain)

parser = shortcodes.Parser(start=sitecore_config.START, end=sitecore_config.END, esc=sitecore_config.ESC)

register = template.Library()

@register.simple_tag()
def shortcodes(value):
    return ParseShortcodes(value)
