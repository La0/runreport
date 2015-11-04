from django.views.generic import DetailView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from payments.models import PaymentPeriod
from payments.export import PeriodPdfExporter


class PaymentPeriodView(DetailView):
  '''
  Process payment for a specified period
  '''
  template_name = 'payments/period.html'
  context_object_name = 'period'

  def get_queryset(self):
    # Only erroneous period for manager
    periods = PaymentPeriod.objects.filter(club__manager=self.request.user)
    periods = periods.filter(status__in=('expired', 'error'))
    return periods

  def post(self, *args, **kwargs):
    # Process payment
    period = self.get_object()
    period.pay()

    return HttpResponseRedirect(reverse('club-manage', args=(period.club.slug, )))

class PaymentPeriodExport(DetailView):
  '''
  Export a period bill as PDF
  '''

  def get_queryset(self):
    # Only erroneous period for manager
    periods = PaymentPeriod.objects.filter(club__manager=self.request.user)
    periods = periods.filter(status='paid')
    return periods

  def render_to_response(self, context, *args, **kwargs):
    period = self.get_object()

    # Init response
    resp = HttpResponse(content_type='application/pdf')
    date_fmt = '%d/%m/%Y'
    resp['Content-Disposition'] = 'attachment; filename="Bill %s - %s - RunReport.pdf"' % (period.start.strftime(date_fmt), period.end.strftime(date_fmt))

    # Build pdf directly into response stream
    export = PeriodPdfExporter(period)
    export.render(resp)

    return resp
