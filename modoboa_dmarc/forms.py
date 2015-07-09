"""Custom forms."""

from django import forms
from django.utils import timezone


class ReportOptionsForm(forms.Form):

    """Report display options."""

    current_year = forms.IntegerField(widget=forms.widgets.HiddenInput)
    current_week = forms.IntegerField()
    query = forms.ChoiceField(
        choices=[("previous", "Previous"), ("next", "Next")])
    resolve_hostnames = forms.BooleanField(
        initial=False, required=False)

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(ReportOptionsForm, self).__init__(*args, **kwargs)
        if not args:
            year, week, day = timezone.now().isocalendar()
            self.fields["current_year"].initial = year
            self.fields["current_week"].initial = week
