#- coding: utf-8
from models import RunReport, RunSession, SESSION_TYPES
from datetime import date
from django import forms

TIME_FORMATS = [
  '%H:%M:%S',
  '%H:%M',
  '%Hh%M',
  '%Hh %M',
  '%Hh %Mm %Ss',
  '%Mmin %Ss',
  '%Mmin',
]

class RunReportForm(forms.ModelForm):
  class Meta:
    model = RunReport
    fields = ('comment', )

class RunSessionForm(forms.ModelForm):
  time = forms.TimeField(input_formats=TIME_FORMATS, widget=forms.TextInput(attrs={'placeholder':'hh:mm'}), required=False)
  distance = forms.FloatField(localize=True, widget=forms.TextInput(attrs={'placeholder': 'km'}), required=False)
  class Meta:
    model = RunSession
    fields = ('name', 'comment', 'distance', 'time', 'type', 'race_category')
    widgets = {
      'type' : forms.HiddenInput(),
    }

  def clean(self):
    # Only for race
    if self.cleaned_data['type'] == 'race':

      # Check time & distance are set, for future races
      session_date = self.instance.date or self.prefix # Get the date even if not in db
      if session_date <= date.today() and (self.cleaned_data.get('time', None) is None or self.cleaned_data.get('distance', None) is None):
        raise forms.ValidationError(u"Pour une course passée, renseignez la distance et le temps.")

      # Check race category
      if not self.cleaned_data['race_category']:
        raise forms.ValidationError(u"Sélectionnez un type de course.")

    return self.cleaned_data

  def is_valid(self):
    is_valid = super(RunSessionForm, self).is_valid()
    if not is_valid:
      return False

    # Don't save any empty sesion, but no message for user
    if not self.cleaned_data.get('name', None) and not self.cleaned_data.get('comment', None):
      return False

    return True

class RunSessionAddForm(forms.Form):
  '''
  Form to create manually a new empty session
  '''
  date = forms.DateField()
  type = forms.ChoiceField(required=False, choices=SESSION_TYPES)

  def __init__(self, user, *args, **kwargs):
    self.user = user
    super(RunSessionAddForm, self).__init__(*args, **kwargs)

  def clean_date(self):

    # Check date is free
    if RunSession.objects.filter(report__user=self.user, date=self.cleaned_data['date']):
      raise forms.ValidationError('Une séance existe déjà à cette date.')

    return self.cleaned_data['date']
