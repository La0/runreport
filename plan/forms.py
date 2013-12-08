# coding=utf-8
from django import forms
from plan.models import Plan, PlanSession
from helpers import nameize

WEEK_CHOICES = tuple([(i,i) for i in range(1,6)])

class PlanCreationForm(forms.Form):
  name = forms.CharField()
  week = forms.ChoiceField(choices=WEEK_CHOICES)

  def __init__(self, creator=None, *args, **kwargs):
    self.creator = creator
    super(PlanCreationForm, self).__init__(*args, **kwargs)

  def clean_name(self):
    '''
    Check the slug is not already used for this creator
    '''
    name = self.cleaned_data['name']
    if Plan.objects.filter(slug=nameize(name), creator=self.creator).count() > 0:
      raise forms.ValidationError(u'Nom de plan déja utilisé')

    return name


class PlanSessionForm(forms.ModelForm):
  
  class Meta:
    model = PlanSession
    exclude = ('week', 'day', )
