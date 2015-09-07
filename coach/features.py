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
    _add(_('Monthly stats'), _('View monthly statistics about your sessions, distance, time cumulated.')),
    _add(_('Share your sessions details'), _('Share all your sport sessions with your friends, trainers, ...')),
    _add(_('Join a club and communicate with your trainer'), _('Comment every session, just with your trainer, or with all your friends.')),
    _add(_('Track your sport sessions'), _('Use a modular calendar view to track every detail of your sport sessions.')),
    _add(_('Garmin Synchronisation'), _('Use all your Garmin Connect data to automatically create sport sessions.'), premium=True),
    _add(_('Strava Synchronisation'), _('Use all your Strava data to automatically create sport sessions.'), premium=True),
    _add(_('Detailed privacy control'), _('Hide some parts of your public profile;'), premium=True),
    _add(_('Google Calendar Export'), _('Automatic export of your sessions in a Google Calendar, so you can get all your calendars in one place & synchronized on your smartphone.'), new=True, premium=True),
    _add(_('Write blog posts'), _('Publish some race reports, training plans details, directly on your public profile. Optimised forsharing on Facebook.'), new=True, premium=True),
    _add(_('Detailed weekly stats'), _('Get some more detailed views of your statistics.'), new=True, premium=True),
  ]
  trainers = [
    _add(_('Be notified of your athletes sessions'), _('Receive notifications when a user publish a week or a session in a plan.')),
    _add(_('Manage your athletes with a powerful interface'), _('List, manage and track easily all your athletes in our powerful web interface.')),
    _add(_('Talk directly and privately with your athletes'), _('Send private messages & comments to all your athletes directly from RunReport.')),
    _add(_('Easily create training plans'), _('Create training plans spanning on multiple weeks with a powerful interface'), new=True),
    _add(_('Send training plans to your athletes in one click'), _('Your athletes receive the plans directly integrated in their calendars.'), new=True),
    _add(_('Maximum Athletes in a club'), _('A free club has 10 athletes maximum. To support more athletes, use a premium club account.'), offers=[10, 100, 1000]),
    _add(_('Create mailing lists for your club & athletes groups.'), _('Send emails to all your athletes in groups or in your club using our new mailing lists.'), premium=True, new=True),
    _add(_('Add your club logo on your pages'), _('Customize your logo pages & athletes menu.'), premium=True, new=True),
    _add(_('Manage your athletes subscriptions'), _('Track the medical certificates & registration details of your athletes through RunReport.'), premium=True, new=True),
  ]

  return {
    'features' : {
      'runners' : filter(None, runners),
      'trainers' : filter(None, trainers),
    }
  }
