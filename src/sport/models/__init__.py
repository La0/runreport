# coding=utf-8
from django.utils.translation import ugettext_lazy as _
SESSION_TYPES = (
    ('training', _('Training')),
    ('race', _('Race')),
    ('rest', _('Rest')),
)

from .organisation import SportWeek, SportDay, RaceCategory
from .sport import Sport, SportSession
