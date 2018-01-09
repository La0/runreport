from django.views.generic import UpdateView
from .mixins import MessageReloadMixin, MessageOwned, MessageSessionMixin
from messages.forms import MessageTextForm


class MessageEdit(MessageReloadMixin, MessageOwned, UpdateView):
    template_name = 'messages/edit.html'
    form_class = MessageTextForm

    def form_valid(self, form):
        # Increment revision
        message = form.save(commit=False)
        message.revision += 1
        message.save()

        return self.reload(message.conversation)
