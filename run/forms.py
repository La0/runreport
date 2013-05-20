from models import RunReport, RunSession
from django import forms

class RunReportForm(forms.ModelForm):
  class Meta:
    model = RunReport
    fields = ('comment', )

class RunSessionForm(forms.ModelForm):
  class Meta:
    model = RunSession
    fields = ('name', 'comment', 'distance', 'time')

  def is_valid(self):
    is_valid = super(RunSessionForm, self).is_valid()
    if not is_valid:
      return False

    # Don't save any empty sesion, but no message for user
    if not self.cleaned_data.get('name', None) and not self.cleaned_data.get('comment', None):
      return False

    return True
