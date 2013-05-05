from models import RunReport
from django import forms

class RunReportForm(forms.ModelForm):
  class Meta:
    model = RunReport
    fields = ('comment', )
