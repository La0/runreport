from django.views.generic import TemplateView
from run.models import RunSession, RaceCategory
from datetime import date

class RacesView(TemplateView):
  template_name = 'users/races.html'

  def get_context_data(self):
    context = super(RacesView, self).get_context_data()
    context.update(self.get_races())
    return context

  def get_races(self):
    # List races
    all_races = RunSession.objects.filter(report__user=self.request.user, type='race', date__lte=date.today())

    # Extract the categories
    cat_ids= [r['race_category'] for r in all_races.values('race_category').distinct() if r['race_category']]
    categories = RaceCategory.objects.filter(pk__in=cat_ids).order_by('name')

    # Categorize races
    races = {}
    for c in categories:
      races[c.id] = all_races.filter(race_category=c).order_by('time')

    return {
      'races' : races,
      'categories' : categories,
    }
