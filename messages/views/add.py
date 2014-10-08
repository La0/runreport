from django.views.generic.edit import CreateView
from messages.forms import MessageTextForm
from mixins import MessageSessionReload, MessageSessionMixin

class MessageSessionAdd(MessageSessionMixin, MessageSessionReload, CreateView):
  template_name = 'messages/add/session.html'
  form_class = MessageTextForm

  def get_context_data(self, *args, **kwargs):
    context = super(MessageSessionAdd, self).get_context_data(*args, **kwargs)
    context['session'] = self.get_session()
    return context

  def form_valid(self, form):
    self.get_session()

    # Save a new message
    message = form.save(commit=False)
    message.session = self.session
    message.sender = self.request.user
    message.recipient = self.session.day.week.user
    message.save()

    return self.reload(self.session)
