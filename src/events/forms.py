from django import forms
from events.models import Place


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('name', 'address', 'city', 'zipcode')
