from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from sport.gcal import GCalSync
from sport.tasks import sync_gcal

class GCalOauthView(TemplateView):
  template_name = 'users/gcal/oauth.html'

  def dispatch(self, *args, **kwargs):
    action = self.kwargs.get('action')

    # Check oauth
    self.gc = GCalSync(self.request.user)
    if self.request.user.gcal_token:

      # Build runreport calendar
      if not self.request.user.gcal_id:
        self.gc.create_calendar('RunReport')

      # Delete all traces
      if action == 'delete':
        self.gc.cleanup()

    else:

      # First step: redirect to Google
      if action == 'redirect':
        return HttpResponseRedirect(self.gc.get_auth_url())

      # Second step: exchange code for token
      code = self.request.GET.get('code')
      if code:
        self.gc.exchange_token(code)

        # Create calendar
        self.gc.create_calendar('RunReport')

        # Init import in new calendar
        sync_gcal.delay(self.request.user)

    return super(GCalOauthView, self).dispatch(*args, **kwargs)

  def get_context_data(self, *args, **kwargs):
    context = super(GCalOauthView, self).get_context_data(*args, **kwargs)

    # List calendars
    cal_id = self.request.user.gcal_id
    if self.request.user.has_gcal() and cal_id:
      context['calendar'] = self.gc.get_calendar(cal_id)

    return context
