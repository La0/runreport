from __future__ import absolute_import

from celery import shared_task

@shared_task
def subscribe_athlete(club, email, first_name, last_name):
  '''
  Subscribe automatically a new athlete
  '''
  from users.models import Athlete
  from club.models import ClubMembership

  # Check existing user
  defaults = {
    'first_name' : first_name,
    'last_name' : last_name,
  }
  user, created = Athlete.objects.get_or_create(email=email, defaults=defaults)
  if not created:
    return

  # Build a unique username
  # TODO

  # Build an avatar for new user
  user.build_avatar()
  user.save()

  # Create athlete club membership
  defaults = {
    'role' : 'athlete',
  }
  ClubMembership.objects.get_or_create(club=club, user=user, defaults=defaults)

  # Send an email to user
  # with direct activation link
  # TODO
