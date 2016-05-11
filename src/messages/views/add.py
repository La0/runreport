from django.views.generic.edit import CreateView
from messages.forms import MessageTextForm
from mixins import MessageReloadMixin, MessageSessionMixin, MessageUserMixin, ConversationMixin, MessageWeekMixin, MessagePostMixin
from messages.models import Conversation, TYPE_MAIL

class MessageUserAdd(MessageUserMixin, MessageReloadMixin, CreateView):
  template_name = 'messages/add/user.html'
  form_class = MessageTextForm

  def get_context_data(self, *args, **kwargs):
    context = super(MessageUserAdd, self).get_context_data(*args, **kwargs)
    context['member'] = self.get_member()
    return context

  def form_valid(self, form):
    self.get_member()

    # Create a new conversation
    conversation = Conversation.objects.create(type=TYPE_MAIL, mail_recipient=self.member)

    # Save a new message for user
    message = form.save(commit=False)
    message.conversation = conversation
    message.writer = self.request.user
    message.save()

    # Add notifications
    conversation.notify(message)

    return self.reload()

class MessageSessionAdd(MessageSessionMixin, MessageReloadMixin, CreateView):
  template_name = 'messages/add/session.html'
  form_class = MessageTextForm

  def get_context_data(self, *args, **kwargs):
    context = super(MessageSessionAdd, self).get_context_data(*args, **kwargs)
    context['type'] = self.kwargs['type']
    return context

  def form_valid(self, form):
    self.get_session()

    # Init a conversation
    type = self.kwargs['type']
    types = {
      'private' : self.session.comments_private,
      'public' : self.session.comments_public,
    }
    conversation = types[type]

    # Build a conversation when none exists
    if not conversation:
      conversation = self.session.build_conversation(type)

    # Save a new comment
    message = form.save(commit=False)
    message.writer = self.request.user
    message.conversation = conversation
    message.save()

    # Add notifications
    conversation.notify(message)

    return self.reload(conversation)

class MessageWeekAdd(MessageWeekMixin, MessageReloadMixin, CreateView):
  template_name = 'messages/add/week.html'
  form_class = MessageTextForm

  def get_context_data(self, *args, **kwargs):
    context = super(MessageWeekAdd, self).get_context_data(*args, **kwargs)
    context['week'] = self.get_week()
    return context

  def form_valid(self, form):
    self.get_week()

    # Add a comment to this week
    message = self.week.add_comment(form.cleaned_data['message'], self.request.user)

    return self.reload(message.conversation)

class MessagePostAdd(MessagePostMixin, MessageReloadMixin, CreateView):
  template_name = 'messages/add/post.html'
  form_class = MessageTextForm

  def get_context_data(self, *args, **kwargs):
    context = super(MessagePostAdd, self).get_context_data(*args, **kwargs)
    context['post'] = self.get_post()
    return context

  def form_valid(self, form):
    self.get_post()

    # Add a comment to this week
    message = self.post.add_comment(form.cleaned_data['message'], self.request.user)

    return self.reload(message.conversation)

class ConversationAdd(ConversationMixin, MessageReloadMixin, CreateView):
  template_name = 'messages/add/conversation.html'
  form_class = MessageTextForm

  def form_valid(self, form):
    self.get_conversation()

    # Save a new comment
    message = form.save(commit=False)
    message.writer = self.request.user
    message.conversation = self.conversation
    message.save()

    # Add notifications
    self.conversation.notify(message)

    return self.reload(self.conversation)

