from django import forms
from messages.models import Message
from django.utils.translation import ugettext_lazy as _


class MessageTextForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('message', )

    def __init__(self, *args, **kwargs):
        super(MessageTextForm, self).__init__(*args, **kwargs)

        # Add placeholder to message
        self.fields['message'].widget.attrs['placeholder'] = _(
            'Write your message here...')


class ContactForm(forms.Form):
    email = forms.EmailField(label=_('Your email'))
    name = forms.CharField(label=_('Your name'))
    message = forms.CharField(label=_('Your message'), widget=forms.Textarea())
