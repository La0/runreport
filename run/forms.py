from models import RunSession, RunReport
from django import forms
from django.forms.models import modelformset_factory

class RunReportForm(forms.ModelForm):
  class Meta:
    model = RunReport
    fields = ('comment', )

# Init Form set factory
RunSessionFormSet = modelformset_factory(RunSession, fields=('comment', 'name', ), extra=0)
