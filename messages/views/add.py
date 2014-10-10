from django.views.generic.edit import CreateView
from messages.forms import MessageTextForm, MessageForm
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
    message.private = True # Always private
    message.save()

    # Add notifications
    message.notify()

    return self.reload()

class MessageSessionAdd(MessageSessionMixin, MessageReloadMixin, CreateView):
  template_name = 'messages/add/session.html'
  form_class = MessageForm

  def get_initial(self, *args, **kwargs):
    args = super(MessageSessionAdd, self).get_initial(*args, **kwargs)

    # For trainer, the comment is private by default
    # or when asking in url
    self.get_session()
    if self.is_trainer() or (self.is_owner() and self.kwargs.get('type', None) == 'private'):
      args['private'] = True

    return args

  def get_context_data(self, *args, **kwargs):
    context = super(MessageSessionAdd, self).get_context_data(*args, **kwargs)
    context['session'] = self.get_session()
    context['has_private'] = self.has_private()
    return context

  def form_valid(self, form):
    self.get_session()

    # Save a new comment
    message = form.save(commit=False)
    message.session = self.session
    message.sender = self.request.user
    message.recipient = self.session.day.week.user
    if not self.has_private():
      message.private = False
    message.save()

    # Add notifications
    message.notify()

    return self.reload(self.session, message.private)
