from django import forms
from core.models import WaitlistEntry

class WaitlistForm(forms.ModelForm):
    class Meta:
        model = WaitlistEntry
        fields = ['email']
