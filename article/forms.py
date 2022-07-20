from django import forms

class FilterForm(forms.Form):
    selected_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'id': 'selected_date',
                'type': 'date'
            }
        )
    )