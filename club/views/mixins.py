from club.models import Club
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

class ClubMixin(object):
  """
  View mixin which verifies that:
    * loads a club from slug kwargs
    * check the logged in user is a club trainer
    * or an admin
  """
  def dispatch(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    # Load club
    self.club = get_object_or_404(Club, slug=kwargs['slug'])

    # Check we have a trainer or an admin
    if not request.user.is_staff:
      try:
        request.user.memberships.get(club=self.club, role="trainer")
      except:
        raise PermissionDenied

    return super(ClubMixin, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(ClubMixin, self).get_context_data(**kwargs)
    context['club'] = self.club
    return context


