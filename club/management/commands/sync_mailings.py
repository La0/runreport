from django.core.management.base import BaseCommand
from club.models import Club
from users.models import Athlete
from coach.mailman import MailMan

class Command(BaseCommand):

  def handle(self, *args, **kwargs):
    self.mm = MailMan()

    # Global mailing
    global_ml = 'all'
    extra = {
      'default_member_action' : 'discard', # members can't send messages
      'default_nonmember_action' : 'discard', # non-members can't send messages
    }
    self.mm.create_list(global_ml, 'Membres RunReport', extra_settings=extra)
    for u in Athlete.objects.filter(is_active=True):
      u.subscribe_mailing(global_ml)
      print '[%s] %s' % (global_ml, u)

    # Sync all clubs
    for club in Club.objects.order_by('name'):
      print 'Club %s' % club

      # Create mailing list
      if not club.mailing_list:
        club.create_mailing_list()
        print ' > Created mailing'

      # Sync the club
      emails = club.clubmembership_set.exclude(role__in=('prospect', 'archive'))
      emails = emails.values_list('user__email', flat=True)
      self.sync_mailing(club.mailing_list, emails)

      # Sync all club groups
      for g in club.groups.all():
        print 'ClubGroup %s' % g

        # Create mailing list
        if not g.mailing_list:
          g.create_mailing_list()
          print ' > Created mailing'

        # Sync the group
        emails = g.members.values_list('user__email', flat=True)
        self.sync_mailing(g.mailing_list, emails)

  def sync_mailing(self, list_name, emails_db):
    '''
    Sync a mailing list for a Club or ClubGroup
    '''
    emails_db = map(lambda x:x.lower(), emails_db)

    # Retrieve list
    l = self.mm.get_list(list_name)
    emails_ml = [m.email.lower() for m in  l.members]

    # Add missing active members
    for m in emails_db:
      if m in emails_ml:
        continue
      u = Athlete.objects.get(email=m)
      u.subscribe_mailing(l.list_name)
      print ' > Add member %s' % m

    # Remove useless users
    emails_ml = set([m.email.lower() for m in  l.members])
    diff = emails_ml.difference(emails_db)
    for m in diff:
      self.mm.unsubscribe(l.list_name, m)
      print ' > Remove %s' % m
