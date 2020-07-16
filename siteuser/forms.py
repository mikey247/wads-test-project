from django import forms
from django.utils.translation import ugettext_lazy as _

from wagtail.users.forms import UserEditForm, UserCreationForm


class CustomUserEditForm(UserEditForm):
    country = forms.CharField(required=True, label=_("Country"))
    twitter = forms.CharField(required=False, label=_('Twitter handle'))


class CustomUserCreationForm(UserCreationForm):
    country = forms.CharField(required=True, label=_("Country"))
    twitter = forms.CharField(required=False, label=_('Twitter handle'))
                        
