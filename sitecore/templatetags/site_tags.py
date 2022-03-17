from datetime import date
from django import template
from wagtail.core.models import Page, Site

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    
    if 'request' in context and context['request'] is not None:
        site = Site.find_for_request(context['request'])
    else:
        site = Site.objects.get(is_default_site=True)
        
    return {
        'site': site,
        'root_page_id': site.root_page_id,
        'root_page': Page.objects.get(pk=site.root_page_id)
    }
    

def has_menu_children(page):
    return page.get_children().live().in_menu().exists()


@register.inclusion_tag('sitecore/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, search_query='', transparent=False, calling_page=None):
    """
    Retrieves the top menu items - the immediate children of the root page.
    The has_menu_children method is necessary because the bootstrap menu requires
    a dropdown class to be applied to a parent.
    """
    
    menuitems = parent.get_children().live().in_menu().specific()
    for menuitem in menuitems:
        menuitem.show_dropdown = has_menu_children(menuitem)
        # We don't directly check if calling_page is None since the template
        # engine can pass an empty string to calling_page
        # if the variable passed as calling_page does not exist.
        menuitem.active = (calling_page.url.startswith(menuitem.url)
                           if calling_page else False)
        

    # build a the navbar configuration for this page
    site_settings = context['settings']['sitecore']['SiteSettings']
    
    navcfg = {
        'brand_logo': site_settings.brand_logo,
        'brand_icon': site_settings.brand_icon,
        'brand_name': site_settings.brand_name,
        'brand_link':  site_settings.brand_link,
        'textmode': site_settings.navbar_text_colour_mode,
        'bg': site_settings.navbar_background_colour,
        'transparent': transparent,
        'outerclass': site_settings.navbar_outer_class,
    }

    # 'request' is required by the pageurl tag that we want to use within this template
    return {
        'parent': parent,
        'calling_page': calling_page,
        'search_query': search_query,
        'menuitems': menuitems,
        'navcfg': navcfg,
        'context': context,
        'path': context['request'].path if 'request' in context and context['request'] is not None else '/',
    }


# Retrieves the children of the top menu items for the drop downs
@register.inclusion_tag('sitecore/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent, menu_id):
    menuitems_children = parent.get_children()
    menuitems_children = menuitems_children.live().in_menu()
    return {
        'parent': parent,
        'menuitems_children': menuitems_children,
        'menu_id': menu_id,
    }


# Renders the page taggit tags as collection of labels
@register.inclusion_tag('sitecore/tags/taggit_list.html', takes_context=True)
def taggit_list(context, page_tags, selected_tag=None, show_count=False):
   return {
       'tags': page_tags,
       'selected': selected_tag,
       'show_count': show_count,
   }


# Renders the social share buttons for the page as collection of icons
@register.inclusion_tag('sitecore/tags/social_share_list.html', takes_context=True)
def social_share_list(context, page):
   return {
       'request': context['request'],
       'page': page,
   }


# Renders the page pagination block based on the paginator resource
@register.inclusion_tag('sitecore/tags/index_pagination.html', takes_context=True)
def index_pagination(context, page_res, page_range, url_path, url_params=''):
   return {
       'page_res': page_res,
       'page_range': page_range,
       'url_path': url_path,
       'url_params': url_params,
   }


# Renders the page author (using author alias if provided) with published_date (or revised if present) in simple clean one-line
@register.inclusion_tag('sitecore/tags/page_meta_summary.html', takes_context=True)
def page_meta_summary(context, page, div_class='page-meta'):
    return {
        'page': page,
    }


# Renders the page author using author alias if provided; othjerwise fallback to owner.get_full_name; fallback to owner (username)
@register.inclusion_tag('sitecore/tags/page_author.html', takes_context=True)
def page_author(context, page, div_class='page-author'):
    return {
        'page': page,
        'div_class': div_class,
    }


# Renders the page creation/first published datetime
@register.inclusion_tag('sitecore/tags/page_date_published.html', takes_context=True)
def page_date_published(context, page, div_class='page-date-published'):
    return {
        'page': page,
        'div_class': div_class,
    }


# Renders the page last revised datetime
@register.inclusion_tag('sitecore/tags/page_date_revised.html', takes_context=True)
def page_date_revised(context, page, div_class='page-date-revised'):
    return {
        'page': page,
        'div_class': div_class,
    }


# Renders a badge representing the content type; article/event/etc.
@register.inclusion_tag('sitecore/tags/page_content_type.html', takes_context=True)
def page_content_type(context, page, div_class='page-content-type'):
    return {
        'page': page,
        'div_class': div_class,
    }


