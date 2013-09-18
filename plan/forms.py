from django import forms
from plan.models import PlanSession

WEEK_CHOICES = tuple([(i,i) for i in range(1,6)])

class PlanCreationForm(forms.Form):
  name = forms.CharField()
  start = forms.DateField(required=False)
  week = forms.ChoiceField(choices=WEEK_CHOICES)

class PlanSessionForm(forms.ModelForm):
  
  class Meta:
    model = PlanSession
    exclude = ('week', 'day', )
