from coach.mixins import JsonResponseMixin, JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from messages.models import Message

class MessageOwned(object):
  # Message must be owned by logged user

  def get_object(self):
    return get_object_or_404(Message, pk=self.kwargs['message_id'], sender=self.request.user)


class MessageSessionReload(JsonResponseMixin):

  def reload(self, session=None):
    # Reload boxes & close modal
    self.json_options = [JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML, ]
    if session and session.day.week.user == self.request.user:
      date = session.day.date
      self.json_boxes = {
        'session-%s-%d' % (date, session.pk) : reverse('sport-session-edit', args=(date.year, date.month, date.day, session.pk,)),
      }

    return self.render_to_response({})
