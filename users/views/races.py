from django.views.generic import TemplateView
from django.db.models import Sum, Count
from sport.models import SportSession, RaceCategory, SportDay
from datetime import date

class RacesView(TemplateView):
  template_name = 'users/races.html'

  def get_context_data(self):
    context = super(RacesView, self).get_context_data()
    context.update(self.get_races())
    return context

  def get_races(self):

    # List races days
    race_days = SportDay.objects.filter(week__user=self.request.user, sessions__type='race')
    future_races = race_days.filter(date__gt=date.today()).order_by('date')
    past_races = race_days.filter(date__lte=date.today())

    # Extract the categories from past_races
    cat_ids = [r['sessions__race_category'] for r in past_races.values('sessions__race_category').distinct() if r['sessions__race_category']]
    categories = dict([(c.id, c) for c in RaceCategory.objects.filter(pk__in=cat_ids).order_by('name')])

    # Sum sessions time & distance per race
    past_races = past_races.annotate(time_total=Sum('sessions__time'), distance_total=Sum('sessions__distance'), nb_sessions=Count('sessions'))

    '''
    for c in categories:
      races[c.id] = past_races.filter(sessions__race_category=c).order_by('time_total')
    '''

    # Categorize races
    # Smartwer way : the past_races query is evaluated here
    races = {}
    for r in past_races:
      for c in r.sessions.filter(type='race').values('race_category').distinct():
        cat_id = c['race_category']
        cat = categories[cat_id]
        if cat_id not in races:
          races[cat_id] = []
        races[cat_id].append(r)

    return {
      'future_races' : future_races,
      'races' : races,
      'categories' : categories,
    }
