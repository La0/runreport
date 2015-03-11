from django.views.generic import View
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from coach.mixins import JsonResponseMixin
from plan.models import PlanSessionApplied
from datetime import datetime


class MovePlanSession(JsonResponseMixin, View):
    '''
    Move a user plan session
    to another day
    '''

    def post(self, *args, **kwargs):

        # Fetch User plan session
        try:
          psa = PlanSessionApplied.objects.get(pk=self.request.POST['psa'], application__user=self.request.user)
        except Exception:
          raise Http404('Invalid plan session')

        # Check date
        try:
          dt = int(self.request.POST['date'])
          date = datetime.fromtimestamp(dt).date()
        except Exception:
          raise Http404('Invalid date')

        # Move the plan session only
        psa.move(date)

        return HttpResponseRedirect(reverse('report-day', args=(date.year, date.month, date.day)))
