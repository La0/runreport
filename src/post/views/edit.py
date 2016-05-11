from django.views.generic import UpdateView, CreateView, ListView, DetailView
from .mixins import PostWriterMixin
from runreport.mixins import JsonResponseMixin, JSON_OPTION_ONLY_AJAX
from sport.models import SportSession
from post.forms import YearMonthForm
from datetime import date

class PostListView(PostWriterMixin, ListView):
  context_object_name = 'posts'
  template_name = 'post/list.html'

class PostCreateView(PostWriterMixin, JsonResponseMixin, CreateView):
  json_options = [JSON_OPTION_ONLY_AJAX, ]

class PostEditView(PostWriterMixin, JsonResponseMixin, UpdateView):
  json_options = [JSON_OPTION_ONLY_AJAX, ]

class PostSessionsView(PostWriterMixin, JsonResponseMixin, DetailView):
  template_name = 'post/sessions.html'

  def post(self, request, *args, **kwargs):
    self.object = self.get_object() # load post first

    # Add a session ?
    if 'add' in self.request.POST:
      session = SportSession.objects.get(day__week__user=self.request.user, pk=self.request.POST['add'])
      self.object.sessions.add(session)

    # Remove a session ?
    if 'remove' in self.request.POST:
      session = SportSession.objects.get(day__week__user=self.request.user, pk=self.request.POST['remove'])
      self.object.sessions.remove(session)

    return self.render_to_response(self.get_context_data())

  def get_context_data(self, *args, **kwargs):
    context = super(PostSessionsView, self).get_context_data(*args, **kwargs)
    context.update(self.load_date_form())
    context.update(self.load_user_sessions())
    return context


  def load_date_form(self):
    if 'switch' in self.request.POST:
      # Use date from POST
      self.date = date(year=int(self.request.POST['date_year']), month=int(self.request.POST['date_month']), day=int(self.request.POST['date_day']))
    else:
      # Defaults to today
      self.date = date.today()
    data = {
      'date' : self.date,
    }
    form = YearMonthForm(self.request.user, data=data)
    return {
      'date' : self.date,
      'date_form' : form,
    }

  def load_user_sessions(self):
    '''
    List user sport sessions, one month at a time
    Default to current month
    '''
    sessions = SportSession.objects.filter(day__week__user=self.request.user)
    sessions = sessions.filter(day__date__month=self.date.month, day__date__year=self.date.year)
    sessions = sessions.prefetch_related('day', 'day__week')
    sessions = sessions.order_by('day__date')

    return {
      'user_sessions' : sessions,
      'post_sessions' : self.object.sessions.values_list('pk', flat=True),
    }
