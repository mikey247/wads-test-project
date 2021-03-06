from datetime import date
from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('article/tags/article_meta.html')
def article_meta(article): 
   return {
      'article': article,
   }


# Renders the article page summary as blog listing entry
@register.inclusion_tag('article/tags/article_blog_summary.html', takes_context=True)
def article_blog_summary(context, post, show_taggit=False, taggit_slug=''):
   return {
      'post': post,
      'show_taggit': show_taggit,
      'taggit_slug': taggit_slug,
   }
