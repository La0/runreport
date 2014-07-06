from club.models import ClubInvite

class UserInviteMixin(object):
  invite = None

  def dispatch(self, *args, **kwargs):
    self.check_invite() # Load invite first
    out = super(UserInviteMixin, self).dispatch(*args, **kwargs)
    return out

  def get_context_data(self, *args, **kwargs):
    context = super(UserInviteMixin, self).get_context_data(*args, **kwargs)

    # Add invite if any
    if self.invite:
      context['invite'] = self.invite

    return context

  def check_invite(self):
    # Load a potential invite from session
    try:
      self.invite = ClubInvite.objects.get(slug=self.request.session['invite'])
    except :
      return False
    return True
