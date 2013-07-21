from club.models import Club, ClubMembership
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

class ClubMixin(object):
  """
  View mixin which verifies that:
    * loads a club from slug kwargs
    * check the logged in user is a club trainer
    * or an admin
  """
  def check(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    # Load club
    self.club = get_object_or_404(Club, slug=kwargs['slug'])

    # Check we have a trainer or an admin or a staff member
    if not request.user.is_staff:
      try:
        request.user.memberships.get(club=self.club, role__in=("trainer", "staff"))
      except:
        raise PermissionDenied

    # Load members
    if 'username' in kwargs:
      self.membership = ClubMembership.objects.get(user__username=kwargs['username'], club=self.club)
      self.member = self.membership.user

  def dispatch(self, request, *args, **kwargs):
    self.check(request, *args, **kwargs)
    return super(ClubMixin, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(ClubMixin, self).get_context_data(**kwargs)
    context['club'] = self.club
    return context

class ClubManagerMixin(ClubMixin):
  """
  Previous mixin, but user must be:
    * the manager of the club
  """
  def dispatch(self, request, *args, **kwargs):
    self.check(request, *args, **kwargs)
    if self.club.manager != request.user:
      raise PermissionDenied
    return super(ClubManagerMixin, self).dispatch(request, *args, **kwargs)

class ClubCreateMixin(object):
  """
  Check that the user is:
    * logged in
    * does not already manage a club
  """
  def dispatch(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    if Club.objects.filter(manager=request.user).count() > 0:
      raise PermissionDenied

    return super(ClubCreateMixin, self).dispatch(request, *args, **kwargs)
