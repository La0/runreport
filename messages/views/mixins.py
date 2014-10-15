from coach.mixins import JsonResponseMixin, JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from messages.models import Message, Conversation, TYPE_COMMENTS_PRIVATE, TYPE_COMMENTS_PUBLIC
from sport.models import SportSession
from users.models import Athlete
from django.core.exceptions import PermissionDenied

class MessageOwned(object):
  # Message must be owned by logged user
  def get_object(self):
    return get_object_or_404(Message, pk=self.kwargs['message_id'], writer=self.request.user)

class ConversationMixin(object):
  def get_conversation(self):
    self.conversation = get_object_or_404(Conversation, pk=self.kwargs['conversation_id'])

    # Check this conversation is visible by current user
    self.session = self.conversation.get_session()
    self.privacy = self.session.day.week.user.get_privacy_rights(self.request.user)
    if self.conversation.type not in self.privacy:
      raise PermissionDenied

    return self.conversation

  def get_context_data(self, *args, **kwargs):
    context = super(ConversationMixin, self).get_context_data(*args, **kwargs)
    if not hasattr(self, 'conversation'):
      self.get_conversation()
    context['conversation'] = self.conversation
    return context


class MessageUserMixin(object):
  def get_member(self):
    # Load member
    self.member = get_object_or_404(Athlete, username=self.kwargs['username'])

    # Can't send yourself some messages
    if self.member == self.request.user:
      raise PermissionDenied

    # Check this member is visible by current user
    self.privacy = self.member.get_privacy_rights(self.request.user)
    if 'comments' not in self.privacy:
      raise PermissionDenied

    return self.member

class MessageSessionMixin(object):

  def get_session(self):
    # Load sport session
    self.session = get_object_or_404(SportSession, pk=self.kwargs['session_id'])

    # Check this session is visible by current user
    self.privacy = self.session.day.week.user.get_privacy_rights(self.request.user)
    if 'comments' not in self.privacy:
      raise PermissionDenied

    # Check type of comments is visible by current user
    if 'type' in self.kwargs:
      name = 'comments_%s' % self.kwargs['type']
      if name not in self.privacy:
        raise PermissionDenied

    return self.session

  def is_trainer(self):
    # User is trainer of session owner ?
    session_user = self.session.day.week.user
    return self.request.user.is_trainer(session_user)

  def is_owner(self):
    # User is session owner
    session_user = self.session.day.week.user
    return session_user == self.request.user

  def get_context_data(self, *args, **kwargs):
    context = super(MessageSessionMixin, self).get_context_data(*args, **kwargs)
    context['session'] = self.get_session()
    context['privacy'] = self.privacy
    return context

class MessageReloadMixin(JsonResponseMixin):

  def reload(self, conversation=None):
    # Reload boxes & close modal
    self.json_options = [JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML, ]

    # Reload conversation list for sessions
    if conversation and conversation.type in (TYPE_COMMENTS_PRIVATE, TYPE_COMMENTS_PUBLIC, ):
      session = conversation.get_session()
      name = 'messages-%d' % (session.pk, )
      url = reverse('conversation-list', args=(conversation.pk, ))
      self.json_boxes = {
        name : url,
      }

    return self.render_to_response({})
