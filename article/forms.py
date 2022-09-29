from django import forms
from datetime import datetime

class FilterForm(forms.Form):
    selected_date = forms.DateField(
        required=False,
        widget=forms.SelectDateWidget(
            attrs={
                'id': 'selected_date',
                'type': 'date',
                'class': 'custom-select'
            },
            empty_label=("Year", "Month", "Day"),
            years=[]
        )
        # Order of the select boxes (month, day, year by default) depend on DATE_FORMAT in settings/local.py
    )

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        YEAR = reversed(range(2000, (datetime.now().year+1)))
        self.fields['selected_date'].widget.years = YEAR