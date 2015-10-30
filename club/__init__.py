# coding:utf-8
from django.utils.translation import ugettext_lazy as _

ROLES = (
  ('athlete', _('Athlete')),
  ('trainer', _('Trainer')),
  ('staff', _('Staff')), # For presidents...
  ('archive', _('Archive')),
  ('prospect', _('Prospect')), # For newcomers
  ('delete', _('Delete')), # For real deletion, post archive
)
