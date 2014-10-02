from coach.mixins import JsonResponseMixin, JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML
from django.core.urlresolvers import reverse

class MessageSessionReload(JsonResponseMixin):

  def reload(self, session=None):
    # Reload boxes & close modal
    self.json_options = [JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML, ]
    if session:
      date = session.day.date
      self.json_boxes = {
        'session-%s-%d' % (date, session.pk) : reverse('sport-session-edit', args=(date.year, date.month, date.day, session.pk,)),
      }

    return self.render_to_response({})
