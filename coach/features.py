from django.utils.translation import ugettext_lazy as _


def list_features(only_premium=False):
  '''
  All the RunReport features !
  '''

  def _add(name, description, free=None, premium=False, new=False, offers=None):
    if only_premium and not premium and not offers:
      return None
    return {
      'name' : name,
      'description' : description,
      'free' : free,
      'premium' : premium,
      'new' : new,
      'offers': offers,
    }

  runners = [
    _add(_('Monthly stats'), _('Desc.')),
    _add(_('Share your sessions details'), _('Desc.')),
    _add(_('Join a club and communicate with your trainer'), _('Desc.')),
    _add(_('Track your sport sessions'), _('Desc.')),
    _add(_('Garmin Synchronisation'), _('Desc.'), premium=True),
    _add(_('Strava Synchronisation'), _('Desc.'), premium=True),
    _add(_('Detailed privacy control'), _('Desc.'), premium=True),
    _add(_('Google Calendar Export'), _('Desc.'), new=True, premium=True),
    _add(_('Write blog posts'), _('Desc.'), new=True, premium=True),
    _add(_('Detailed weekly stats'), _('Desc.'), new=True, premium=True),
  ]
  trainers = [
    _add(_('Be notified of your athletes sessions'), _('Desc.')),
    _add(_('Manage your athletes with a powerful interface'), _('Desc.')),
    _add(_('Talk directly and privately with your athletes'), _('Desc.')),
    _add(_('Easily create training plans'), _('Desc.'), new=True),
    _add(_('Send training plans to your athletes in one click'), _('Desc.'), new=True),
    _add(_('Maximum Athletes in a club'), _('Desc.'), offers=[10, 100, 1000]),
    _add(_('Maximum Trainers in a club'), _('Desc.'), offers=[1, 5, 50]),
    _add(_('Create mailing lists for your club & athletes groups.'), _('Desc.'), premium=True, new=True),
    _add(_('Add your club logo on your pages'), _('Desc.'), premium=True, new=True),
    _add(_('Manage your athletes subscriptions'), _('Desc.'), premium=True, new=True),
  ]

  return {
    'features' : {
      'runners' : filter(None, runners),
      'trainers' : filter(None, trainers),
    }
  }
