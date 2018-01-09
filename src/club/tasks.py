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
            pass  # use this username

        i += 1

    # Check existing user
    defaults = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
    }
    user, created = Athlete.objects.get_or_create(
        email=email, defaults=defaults)
    if not created:
        return

    # Build an avatar for new user
    user.build_avatar()
    user.save()

    # Create athlete club membership
    defaults = {
        'role': 'athlete',
    }
    ClubMembership.objects.get_or_create(
        club=club, user=user, defaults=defaults)

    # Create an invite for new user
    data = {
        'sender': club.manager,
        'recipient': email,
        'user': user,
        'club': club,
        'type': 'join',
    }
    invite = ClubInvite.objects.create(**data)
    invite.send()


@shared_task
def group_create_ml(group):
    '''
    Create a mailing list for a group
    '''
    group.create_mailing_list()


@shared_task
def group_delete_ml(group):
    '''
    Delete a mailing list for a group
    '''
    group.delete_mailing_list()


@shared_task
def mail_member_role(membership, role):
    '''
    On role change, send an email to user
    '''
    membership.mail_user(role)


@shared_task
def sync_mailing_membership(membership, add):
    '''
    Sync the mailing list usage
    for a user's membership
    '''
    if add:
        # Add to main
        if membership.club.mailing_list:
            membership.user.subscribe_mailing(membership.club.mailing_list)

        # Add to groups
        for g in membership.groups.filter(mailing_list__isnull=False):
            membership.user.subscribe_mailing(g.club.mailing_list)

    else:
        # Remove from main
        if membership.club.mailing_list:
            membership.user.unsubscribe_mailing(membership.club.mailing_list)

        # Remove from groups
        for g in membership.groups.filter(mailing_list__isnull=False):
            membership.user.unsubscribe_mailing(g.club.mailing_list)
