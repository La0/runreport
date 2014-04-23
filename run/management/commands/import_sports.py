from django.core.management.base import BaseCommand, CommandError
from coach.settings import HOME
from run.models import Sport
import os
import json

class Command(BaseCommand):
  path = HOME + '/run/management/data/sports.json'
  sports = []

  def handle(self, *args, **options):
    if not os.path.exists(self.path):
      raise CommandError('Missing sports data in %s' % self.path)

    # Load
    sports_json = json.loads(open(self.path, 'r').read())
    self.sports = sports_json['dictionary']

    # Depth
    start = self.sports[0]
    start['depth'] = 0
    self.recursive_depth(start)

    # Save in db
    for sport in self.sports:
      try:
        parent = Sport.objects.get(slug=sport['parent']['key'])
      except:
        parent = None
      defaults = {
        'name' : sport['display'],
        'depth' : sport['depth'],
        'parent' : parent,
      }
      s, created = Sport.objects.get_or_create(slug=sport['key'], defaults=defaults)
      print '%s %s at depth %d' % (created and 'Created' or 'Skipped', s.slug, s.depth)

  def recursive_depth(self, parent):
    for s in self.sports:
      if 'parent' not in s or 'level' in s:
        continue
      if s['parent']['key'] == parent['key']:
       s['depth'] = parent['depth'] + 1
       self.recursive_depth(s)
