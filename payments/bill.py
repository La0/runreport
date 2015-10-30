from django.db.models import Count
from django.conf import settings

class Bill(object):
  '''
  Calculate the bill for a set
  of club members
  '''

  counts = {
    'athlete' : 0,
    'staff' : 0,
    'trainer' : 0,
    'archive' : 0,
  }
  stats = {}
  total = 0

  def __init__(self, club=None):
    # Get nb of roles in club
    if club:
      counts = club.clubmembership_set.values('role').annotate(nb=Count('role'))
      self.counts = dict([(c['role'], c['nb']) for c in counts])

  def calc(self):
    '''
    Calc the bill.
    Outputs stats about types
    '''
    # reset
    self.stats = []
    self.total = 0

    roles = ('athlete', 'trainer', 'staff', 'archive', )
    for r in roles:
      s = self.calc_role(r)
      self.total += s['price']
      self.stats.append(s)

    return self.stats

  def calc_role(self, role):
    '''
    Calc cost for a role
    '''
    # Total nb of athletes
    total = self.counts.get(role, 0)

    # Paying accounts
    paying = max(total, 0)

    # Prices & total per role
    unit = settings.PREMIUM_PRICES.get(role, 0)
    price = unit * paying

    return {
      'type' : role,
      'total' : total,
      'paying' : paying,
      'unit' : unit,
      'price' : price,
    }

  def cost_new_role(self, old_role, new_role):
    '''
    Calc the cost of a new role
    using calculated stats & compare to old role
    Outputs:
     * price difference
     * unit price
    '''
    stats_old = self.calc_role(old_role)
    stats_new = self.calc_role(new_role)

    diff = stats_new['unit'] - stats_old['unit']

    return diff, stats_new['unit']
