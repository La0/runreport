from django.views.generic.edit import CreateView
from messages.forms import MessageTextForm
from mixins import MessageReloadMixin, MessageSessionMixin, MessageUserMixin

class MessageUserAdd(MessageUserMixin, MessageReloadMixin, CreateView):
  template_name = 'messages/add/user.html'
  form_class = MessageTextForm

  def get_context_data(self, *args, **kwargs):
    context = super(MessageUserAdd, self).get_context_data(*args, **kwargs)
    context['member'] = self.get_member()
    return context

  def form_valid(self, form):
    self.get_member()

    # Save a new message for user
    message = form.save(commit=False)
    message.sender = self.request.user
    message.recipient = self.member
    message.save()

    # Add notifications
    message.notify()

    return self.reload()

class MessageSessionAdd(MessageSessionMixin, MessageReloadMixin, CreateView):
  template_name = 'messages/add/session.html'
  form_class = MessageTextForm

  def get_context_data(self, *args, **kwargs):
    context = super(MessageSessionAdd, self).get_context_data(*args, **kwargs)
    context['session'] = self.get_session()
    return context

  def form_valid(self, form):
    self.get_session()

    # Save a new comment
    message = form.save(commit=False)
    message.session = self.session
    message.sender = self.request.user
    message.recipient = self.session.day.week.user
    message.save()

    # Add notifications
    message.notify()

    return self.reload(self.session)
