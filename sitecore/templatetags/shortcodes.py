import shortcodes
import html
from django import template
import sitecore.config as cfg
import sitecore.parsers as parsers

### create shortcodes

@shortcodes.register("code", "/code")
def handler(pargs, kwargs, context, content):
    content_html = html.escape(content)
    return '<code>%s</code>' % (content_html)

@shortcodes.register("samp", "/samp")
def handler(pargs, kwargs, context, content):
    try:
        mode = html.escape(pargs[0])
        if mode == 'block':
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
def handler(pargs, kwargs, context, content):
    content_html = html.escape(content)
    return '<var>%s</var>' % (content_html)

@shortcodes.register("del", "/del")
def handler(pargs, kwargs, context, content):
    content_html = html.escape(content)
    return '<del>%s</del>' % (content_html)

@shortcodes.register("ins", "/ins")
def handler(pargs, kwargs, context, content):
    content_html = html.escape(content)
    return '<ins>%s</ins>' % (content_html)

@shortcodes.register("strike", "/strike")
def handler(pargs, kwargs, context, content):
    content_html = html.escape(content)
    return '<s>%s</s>' % (content_html)

@shortcodes.register("kbd")
def handler(pargs, kwargs, context):
    result = []
    for arg in pargs:
        try:
            kbd = html.escape(arg)
        except:
            kbd = "No key specified"
        result.append('<kbd>%s</kbd>' % (kbd))
    return u' '.join(result)

@shortcodes.register("abbr")
def handler(pargs, kwargs, context):
    try:
        title = html.escape(pargs[0])
        abbr = html.escape(pargs[1])
    except:
        raise shortcodes.ShortcodeRenderingError
        
    return '<abbr title="%s">%s</abbr>' % (title,abbr)

@shortcodes.register("span", "/span")
def handler(pargs, kwargs, context, content):
    try:
        classes = html.escape(u' '.join(pargs))
    except:
        classes = u''

    return '<span class="%s">%s</span>' % (classes,content)


# create simple_tag (cleaner processing as we can mark_safe in code rather than a filter chain)

parser = shortcodes.Parser(start=cfg.START, end=cfg.END, esc=cfg.ESC)

register = template.Library()

@register.simple_tag()
def shortcodes(value):
    return parsers.ParseShortcodes(value)

