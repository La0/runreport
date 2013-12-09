#- coding: utf-8
from models import RunReport, RunSession
from datetime import date
from django import forms

class RunReportForm(forms.ModelForm):
  class Meta:
    model = RunReport
    fields = ('comment', )

class RunSessionForm(forms.ModelForm):
  class Meta:
    model = RunSession
    fields = ('name', 'comment', 'distance', 'time', 'type')
    widgets = {
      'distance' : forms.TextInput(attrs={'placeholder': 'km'}),
      'time' : forms.TimeInput(attrs={'placeholder' : 'hh:mm'}),
      'type' : forms.HiddenInput(),
    }

  def clean(self):
    # Only for race
    # Check time & distance are set, for future races
    session_date = self.instance.date or self.prefix # Get the date even if not in db
    if self.cleaned_data['type'] == 'race' and session_date <= date.today() and (self.cleaned_data.get('time', None) is None or self.cleaned_data.get('distance', None) is None):
      raise forms.ValidationError(u"Pour une course passée, renseignez la distance et le temps.")

    return self.cleaned_data

  def is_valid(self):
    is_valid = super(RunSessionForm, self).is_valid()
    if not is_valid:
      return False

    # Don't save any empty sesion, but no message for user
    if not self.cleaned_data.get('name', None) and not self.cleaned_data.get('comment', None):
      return False

    return True
