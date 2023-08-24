from django import forms
from .models import PhraseList

class DistanceValueForm(forms.Form):
    distanceValue = forms.IntegerField(label="Max Distance for Commute", widget=forms.TextInput(attrs={"id":"distanceRange","type":"range", "class":"form-range"}), label_suffix=": ", initial=1, min_value=1, max_value=100, step_size=1)
    

class PhraseListForm(forms.ModelForm):
    class Meta:
        model = PhraseList
        fields = ['user_id', 'phrases']
        widgets = {
            'phrases': forms.TextInput(attrs={'placeholder': 'Enter phrases separated by commas'}),
            'user_id': forms.HiddenInput()
        }
