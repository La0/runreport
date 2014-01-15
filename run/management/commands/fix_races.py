from django.core.management.base import BaseCommand, CommandError
from run.models import RunSession, RaceCategory

class Command(BaseCommand):

  def handle(self, *args, **options):
    '''
    Browse all non categorized races
    and ask for a category.
    '''

    # Build categories shortcuts
    cats = RaceCategory.objects.all().order_by('name')
    self.categories = {}
    for cat in cats:
      self.categories[cat.name] = cat
      self.categories[cat.name.lower()] = cat
      self.categories[cat.name.replace(' ', '').lower()[0:2]] = cat
    for name,cat in self.categories.items():
      print "%s : %s" % (name, cat.name)
    print '-' * 40

    races = RunSession.objects.filter(type='race', race_category=None).order_by('name')
    for r in races:
      self.ask_category(r)

  def ask_category(self, race):
    print "%s le %s par %s" % (race.name, race.date, race.report.user.username)

    cat_name = None
    while cat_name is None:
      cat_name = raw_input(' >> Category ? ')
      if cat_name not in self.categories:
        cat_name = None
        continue

      # Ask for confirmation
      cat = self.categories[cat_name]
      ok = raw_input(' >> %s [y] ? ' % cat.name)
      if ok not in ('', 'y', 'yes',):
        cat_name = None
        continue

      # Save cat
      race.race_category = cat
      race.save()
      print '-' * 40

