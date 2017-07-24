import shortcodes
import html
from django import template
import sitecore.config as cfg
#from sitecore.parsers import ParseMarkdownAndShortcodes, ParseShortcodes
import sitecore.parsers as parsers

### create shortcodes

@shortcodes.register("code", "/code")
def handler(context, content, pargs, kwargs):
    content_html = html.escape(content)
    return '<code>%s</code>' % (content_html)

@shortcodes.register("samp", "/samp")
def handler(context, content, pargs, kwargs):
    try:
        mode = html.escape(pargs[0])
        if mode is 'block':
            enable_pre = True
        else:
            enable_pre = False
    except:
        enable_pre = False
    samp_html = '<samp>%s</samp>' % (content)
    if enable_pre:
        return '<pre>%s</pre>' % (samp_html)
    else:
        return samp_html

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
        raise RenderingError
        
    return '<abbr title="%s">%s</abbr>' % (title,abbr)


# create simple_tag (cleaner processing as we can mark_safe in code rather than a filter chain)

parser = shortcodes.Parser(start=cfg.START, end=cfg.END, esc=cfg.ESC)

register = template.Library()

@register.simple_tag()
def shortcodes(value):
    return parsers.ParseShortcodes(value)

@register.simple_tag()
def markdown_shortcodes(value):
    return parsers.ParseMarkdownAndShortcodes(value)
