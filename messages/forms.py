from django import forms
from messages.models import Message
from django.utils.translation import ugettext_lazy as _

class MessageTextForm(forms.ModelForm):
  class Meta:
    model = Message
    fields = ('message', )

class ContactForm(forms.Form):
  email = forms.EmailField(label=_('Your email'))
  name = forms.CharField(label=_('Your name'))
  message = forms.CharField(label=_('Your message'), widget=forms.Textarea())
