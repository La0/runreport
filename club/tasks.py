from __future__ import absolute_import

from celery import shared_task

@shared_task
def subscribe_athlete(club, email, first_name, last_name):
  '''
  Subscribe automatically a new athlete
  '''
  from users.models import Athlete
  from club.models import ClubMembership, ClubInvite
  from helpers import nameize

  # Build a unique username
  base = '%s_%s' % (nameize(first_name), nameize(last_name))
  i = 1
  username = None
  while username is None:
    username = i == 1 and base or '%s_%d' % (base, i)
    try:
      Athlete.objects.get(username=username)
      username = None
    except Athlete.DoesNotExist:
      pass # use this username

    i += 1

  # Check existing user
  defaults = {
    'username' : username,
    'first_name' : first_name,
    'last_name' : last_name,
  }
  user, created = Athlete.objects.get_or_create(email=email, defaults=defaults)
  if not created:
    return

  # Build an avatar for new user
  user.build_avatar()
  user.save()

  # Create athlete club membership
  defaults = {
    'role' : 'athlete',
  }
  ClubMembership.objects.get_or_create(club=club, user=user, defaults=defaults)

  # Create an invite for new user
  data = {
    'sender' : club.manager,
    'recipient' : email,
    'user' : user,
    'club' : club,
    'type' : 'join',
  }
  invite = ClubInvite.objects.create(**data)
  invite.send()

@shared_task
def group_create_ml(group):
  '''
  Create a mailing list for a group
  '''
  group.create_mailing_list()
