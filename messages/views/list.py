from django.views.generic import ListView
from coach.mixins import JsonResponseMixin
from mixins import MessageSessionMixin

class MessageSessionList(JsonResponseMixin, MessageSessionMixin, ListView):
  template_name = 'messages/_list.html'
  context_object_name = 'messages'
  list_type = None

  def get_context_data(self):
    context = super(MessageSessionList, self).get_context_data()
    context['session'] = self.session
    context['list_type'] = self.list_type
    print context
    return context

  def get_queryset(self):
    session = self.get_session()
    session_user = session.day.week.user

    # Only the session owner
    # or one of its trainer
    # can change the type
    if session_user == self.request.user or self.request.user.is_trainer(session_user):
      self.list_type = self.kwargs.get('type', 'public')
      filters = {
        'all' : {},
        'private' : {
          'private' : True,
        },
        'public' : {
          'private' : False,
        },
      }
      return session.comments.filter(**filters[self.list_type]).order_by('created')

    # By default, Just list public comments
    return session.comments.filter(private=False).order_by('created')
