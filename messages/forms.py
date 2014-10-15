from django import forms
from messages.models import Message

class MessageTextForm(forms.ModelForm):
  class Meta:
    model = Message
    fields = ('message', )
