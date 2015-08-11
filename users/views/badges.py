from __future__ import absolute_import
from badges.views import BadgesView
from users.views.mixins import ProfilePrivacyMixin

class UserBadgesView(ProfilePrivacyMixin, BadgesView):
  '''
  Display badges for a requested user
  '''
  pass
