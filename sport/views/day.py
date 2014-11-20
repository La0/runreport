from sport.forms import SportSessionForm
from sport.models import SportDay, SportSession
from coach.mixins import JsonResponseMixin, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD
from .mixins import SportSessionForms
from django.views.generic import DateDetailView
from django.views.generic.edit import DeleteView
from mixins import CalendarDay
from django.core.urlresolvers import reverse
from datetime import datetime, date, timedelta
from helpers import date_to_week, check_task

class RunCalendarDay(SportSessionForms, CalendarDay, DateDetailView):
  template_name = 'sport/day/edit.html'

  def get_context_data(self, *args, **kwargs):
    context = super(RunCalendarDay, self).get_context_data(*args, **kwargs)
    context['now'] = datetime.now()
    context['forms'] = self.get_sessions_forms(self.day, self.object)

    # Previous week sunday
    week = self.object.week
    diff = timedelta(days=1)
    context['previous_day'] = week.get_date_start() - diff

    # Next week monday
    context['next_day'] = week.get_date_end() + diff

    # Add previous week, not published
    try:
      w, y = date_to_week(date.today() - timedelta(days=7))
      context['previous_week'] = SportWeek.objects.filter(user=self.request.user, year=y, week=w, published=False)
    except:
      context['previous_week'] = None

    # Add friends with activities on the same day
    friends = []
    user = self.get_user()
    if user == self.request.user:
      friends = SportSession.objects.filter(day__date=self.day, day__week__user__in=user.friends.all())
      friends = friends.prefetch_related('day', 'day__week', 'sport', 'day__week__user')
      friends = friends.order_by('day__week__user__first_name')
    context['friends_sessions'] = friends

    # Check task on week
    check_task(week)

    return context

class RunCalendarDayDelete(CalendarDay, JsonResponseMixin, DeleteView, DateDetailView):
  template_name = 'sport/day/delete.html'

  def delete(self, *args, **kwargs):
    '''
    Delete day, then reload
    '''
    self.get_object()
    self.object.delete()
    self.object.rebuild_cache()

    # Configure output to reload page
    self.json_options = [JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD]
    return self.render_to_response({})
