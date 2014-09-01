from django.views.generic import TemplateView
from django.db.models import Sum
from sport.models import SportSession, RaceCategory
from datetime import date

class RacesView(TemplateView):
  template_name = 'users/races.html'

  def get_context_data(self):
    context = super(RacesView, self).get_context_data()
    context.update(self.get_races())
    return context

  def get_races(self):
    # TODO: handle multiple race parts per day (triathlon)

    # List races
    all_races = SportSession.objects.filter(day__week__user=self.request.user, type='race')
    future_races = all_races.filter(day__date__gt=date.today()).order_by('day__date')
    past_races = all_races.filter(day__date__lte=date.today())

    # Extract the categories from past_races
    cat_ids= [r['race_category'] for r in past_races.values('race_category').distinct() if r['race_category']]
    categories = RaceCategory.objects.filter(pk__in=cat_ids).order_by('name')

    # Categorize races
    races = {}
    for c in categories:
      races[c.id] = past_races.filter(race_category=c).order_by('time')

    return {
      'future_races' : future_races,
      'races' : races,
      'categories' : categories,
    }
