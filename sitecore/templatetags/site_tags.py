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
        'root_page': Page.objects.get(pk=root_page_id)
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
    
    menuitems = parent.get_children().live().in_menu()
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


# Renders the page pagination block based on the paginator resource
@register.inclusion_tag('sitecore/tags/pagination.html', takes_context=True)
def pagination(context, page_res, page_range):
   return {
       'page_res': page_res,
       'page_range': page_range,
   }


# Calls render method for page author using page.author as alias if provided; fallback to owner.get_full_name; fallback to owner (username)
@register.inclusion_tag('sitecore/tags/page_author.html', takes_context=True)
def page_author(context, page):
    return {
        'page': page,
    }


# Calls eenders method for page timestamp using creation date and/or modification date
@register.inclusion_tag('sitecore/tags/page_date.html', takes_context=True)
def page_date(context, page):
    return {
        'page': page,
    }
