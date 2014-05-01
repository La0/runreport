# coding=utf-8
SESSION_TYPES = (
  ('training', 'Entrainement'),
  ('race', 'Course'),
  ('rest', 'Repos'),
)

from .organisation import SportWeek, SportDay, RaceCategory
from .sport import Sport
from .garmin import GarminActivity
