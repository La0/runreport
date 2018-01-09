from django.views.generic import FormView
from django.urls import reverse
from messages.forms import ContactForm
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from runreport.mail import MailBuilder


class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm

    def get_success_url(self):
        return reverse('contact', args=('sent', ))

    def get_context_data(self, *args, **kwargs):
        context = super(ContactView, self).get_context_data(*args, **kwargs)
        context['sent'] = self.kwargs.get('sent') == 'sent'
        return context

    def form_valid(self, form):
        '''
        Send email to all admins
        '''
        context = form.cleaned_data
        headers = {
            'Reply-To': context['email'],
        }
        mb = MailBuilder('mail/contact.html')
        mb.subject = _('New contact message')
        mb.to = [email for __, email in settings.ADMINS]
        mail = mb.build(context, headers)
        mail.send()

        return super(ContactView, self).form_valid(form)
