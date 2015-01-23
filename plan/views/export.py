from django.views.generic import DetailView
from django.http import HttpResponse
from plan.export import PlanPdfExporter

class PlanPdfExport(DetailView):
  def get_queryset(self):
    # Allow only user's plans
    return self.request.user.plans.all()


  def render_to_response(self, context, *args, **kwargs):
    plan = context['plan']

    # Init response
    resp = HttpResponse(content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="Plan %s - RunReport.pdf"' % plan.name

    # Build pdf directly into response stream
    export = PlanPdfExporter(plan)
    export.render(resp)

    return resp
