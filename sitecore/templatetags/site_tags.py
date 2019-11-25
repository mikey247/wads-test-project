from datetime import date
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return context['request'].site.root_page


def has_menu_children(page):
    return page.get_children().live().in_menu().exists()


@register.inclusion_tag('tags/top_menu.html', takes_context=True)
def top_menu(context, parent, transparent=False, calling_page=None):
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
        'textmode': site_settings.navbar_text_colour_mode,
        'bg': site_settings.navbar_background_colour,
        'transparent': transparent,
    }

    # 'request' is required by the pageurl tag that we want to use within this template
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        'navcfg': navcfg,
        'request': context['request'],
    }


# Retrieves the children of the top menu items for the drop downs
@register.inclusion_tag('tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent, menu_id):
    menuitems_children = parent.get_children()
    menuitems_children = menuitems_children.live().in_menu()
    return {
        'parent': parent,        
        'menuitems_children': menuitems_children,
        'menu_id': menu_id,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Renders the page taggit tags as collection of labels
@register.inclusion_tag('tags/taggit_list.html', takes_context=True)
def taggit_list(context, page_tags, selected_tag=None, show_count=False): 
   return {
       'tags': page_tags,
       'selected': selected_tag,
       'show_count': show_count,
   }


# Renders the page pagination block based on the paginator resource
@register.inclusion_tag('tags/pagination.html', takes_context=True)
def pagination(context, page_res): 
   return {
       'res': page_res,
   }


# Calls render method for page author using page.author as alias if provided; fallback to owner.get_full_name; fallback to owner (username)
@register.inclusion_tag('tags/page_author.html', takes_context=True)
def page_author(context, page):
    return {
        'page': page,
    }


# Calls eenders method for page timestamp using creation date and/or modification date
@register.inclusion_tag('tags/page_date.html', takes_context=True)
def page_date(context, page):
    return {
        'page': page,
    }


