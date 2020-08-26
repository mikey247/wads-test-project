from datetime import date
from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('article/tags/article_meta.html')
def article_meta(article): 
   return {
       'article': article,
   }


