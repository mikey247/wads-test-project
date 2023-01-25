from django import forms
from django.utils.translation import gettext_lazy as _

from wagtail.users.forms import UserEditForm, UserCreationForm

class CustomUserEditForm(UserEditForm):
    '''
    Defines edit form for Custom User Model, adding extra fields
    '''
    bio = forms.CharField(
        required=False,
        label=_('Bio'),
    )

    team = forms.CharField(
        required=False,
        label=_("Team"),
    )

    job_title = forms.CharField(
        required=False,
        label=_("Job Title"),
    )
    
    country = forms.CharField(
        required=False,
        label=_("Country"),
    )

    twitter = forms.CharField(
        required=False,
        label=_('Twitter handle'),
    )
    
    receive_submission_notify_email = forms.BooleanField(
        required=False,
        label=_('Receive notification of submissions'),
    )

    
class CustomUserCreationForm(UserCreationForm):
    '''
    Defines creation form for Custom User Model, adding extra fields
    '''

    bio = forms.CharField(
        required=False,
        label=_('Bio'),
    )
    
    team = forms.CharField(
        required=False,
        label=_("Team"),
    )
    
    job_title = forms.CharField(
        required=False,
        label=_("Job Title"),
    )

    country = forms.CharField(
        required=False,
        label=_("Country"),
    )
    
    twitter = forms.CharField(
        required=False,
        label=_('Twitter handle'),
    )
    
    receive_submission_notify_email = forms.BooleanField(
        required=False,
        label=_('Receive notification of submissions'),
    )
                        
