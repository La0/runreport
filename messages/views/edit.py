from django.views.generic import UpdateView
from mixins import MessageReloadMixin, MessageOwned, MessageSessionMixin
from messages.forms import MessageForm

class MessageEdit(MessageSessionMixin, MessageReloadMixin, MessageOwned, UpdateView):
  template_name = 'messages/edit.html'
  form_class = MessageForm

  def get_context_data(self, *args, **kwargs):
    context = super(MessageEdit, self).get_context_data(*args, **kwargs)

    # We don't always have a session here
    try:
      self.session = message.session
    except:
      pass
    return context

  def form_valid(self, form):
    # Increment revision
    message = form.save(commit=False)
    message.revision += 1

    # We don't always have a session here
    try:
      self.session = message.session
      if 'comments_private' not in self.privacy:
        message.private = False
    except Exception, e:
      message.private = False

    message.save()

    return self.reload(message.session, message.private)
