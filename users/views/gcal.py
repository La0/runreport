from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from sport.gcal import GCalSync

class GCalOauthView(TemplateView):
  template_name = 'users/gcal/oauth.html'

  def dispatch(self, *args, **kwargs):

    # Check oauth
    self.gc = GCalSync(self.request.user)
    if self.request.user.gcal_token:

      # Build runreport calendar
      if not self.request.user.gcal_id:
        cal = self.gc.create_calendar('RunReport')
        if cal:
          self.request.user.gcal_id = cal['id']
          self.request.user.save()

    else:

      # First step: redirect to Google
      redirect = self.kwargs.get('redirect') == 'redirect'
      if redirect:
        return HttpResponseRedirect(self.gc.get_auth_url())

      # Second step: exchange code for token
      code = self.request.GET.get('code')
      if code:
        self.gc.exchange_token(code)

    return super(GCalOauthView, self).dispatch(*args, **kwargs)

  def get_context_data(self, *args, **kwargs):
    context = super(GCalOauthView, self).get_context_data(*args, **kwargs)

    # List calendars
    context['calendars'] = self.gc.list_calendars()

    return context
