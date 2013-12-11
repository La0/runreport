# coding=utf-8
from django import forms
from plan.models import Plan, PlanSession
from club.models import Club
from helpers import nameize, date_to_day
from datetime import date, timedelta

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

class PlanApplyWeekForm(forms.Form):
  week = forms.ChoiceField()

  def __init__(self, *args, **kwargs):
    super(PlanApplyWeekForm, self).__init__(*args, **kwargs)

    # Build week choices
    start = date_to_day(date.today())
    weeks = []
    for i in range(0,6):
      dt = start + timedelta(days=i*7)
      dt_str = dt.strftime('Semaine %W du %d %B %Y')
      weeks.append((dt,dt_str))
    self.fields['week'].choices = weeks
