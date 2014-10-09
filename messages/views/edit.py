from django.views.generic import UpdateView
from mixins import MessageReloadMixin, MessageOwned
from messages.forms import MessageForm

class MessageEdit(MessageReloadMixin, MessageOwned, UpdateView):
  template_name = 'messages/edit.html'
  form_class = MessageForm

  def form_valid(self, form):
    # Increment revision
    message = form.save(commit=False)
    message.revision += 1
    message.save()

    return self.reload(message.session)
