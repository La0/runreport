from coach.mixins import JsonResponseMixin, JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from messages.models import Message
from sport.models import SportSession
from users.models import Athlete
from django.core.exceptions import PermissionDenied

class MessageOwned(object):
  # Message must be owned by logged user

  def get_object(self):
    return get_object_or_404(Message, pk=self.kwargs['message_id'], sender=self.request.user)

class MessageUserMixin(object):
  def get_member(self):
    # Load member
    self.member = get_object_or_404(Athlete, username=self.kwargs['username'])

    # Can't send yourself some messages
    if self.member == self.request.user:
      raise PermissionDenied

    # Check this member is visible by current user
    privacy = self.member.get_privacy_rights(self.request.user)
    if 'calendar' not in privacy: #TODO: use another right 'message'
      raise PermissionDenied

    return self.member

class MessageSessionMixin(object):

  def get_session(self):
    # Load sport session
    self.session = get_object_or_404(SportSession, pk=self.kwargs['session_id'])

    # Check this session is visible by current user
    privacy = self.session.day.week.user.get_privacy_rights(self.request.user)
    if 'calendar' not in privacy: #TODO: use another right 'message'
      raise PermissionDenied

    return self.session


class MessageReloadMixin(JsonResponseMixin):

  def reload(self, session=None):
    # Reload boxes & close modal
    self.json_options = [JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML, ]

    if session:
      date = session.day.date
      session_user = session.day.week.user

      # Always reload only messages for member
      name = 'messages-%d' % (session.pk, )
      url = reverse('message-session-list', args=(session.pk,)),
      self.json_boxes = {
        name : url,
      }

    return self.render_to_response({})
