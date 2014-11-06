# coding=utf-8
from django.utils.translation import ugettext_lazy as _
SESSION_TYPES = (
  ('training', _('training')),
  ('race', _('race')),
  ('rest', _('rest')),
)

from .organisation import SportWeek, SportDay, RaceCategory
from .sport import Sport, SportSession
