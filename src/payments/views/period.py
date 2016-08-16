from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from payments.export import PeriodPdfExporter
from payments.views.mixins import PaymentPeriodMixin

class PaymentPeriodView(PaymentPeriodMixin):
  '''
  Process payment for a specified period
  '''
  template_name = 'payments/period.html'
  context_object_name = 'period'

  def get_queryset(self):
    # Only erroneous period for manager
    periods = super(PaymentPeriodView, self).get_queryset()
    periods = periods.filter(status__in=('expired', 'error'))
    return periods

  def post(self, *args, **kwargs):
    # Process payment
    period = self.get_object()
    period.pay()

    return HttpResponseRedirect(reverse('club-manage', args=(period.club.slug, )))

class PaymentPeriodExport(PaymentPeriodMixin):
  '''
  Export a period bill as PDF
  '''

  def get_queryset(self):
    # Only erroneous period for manager
    periods = super(PaymentPeriodExport, self).get_queryset()
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
