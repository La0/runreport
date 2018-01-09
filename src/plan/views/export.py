from django.views.generic import DetailView
from django.http import HttpResponse
from plan.export import PlanPdfExporter
from plan.export import PlanIcsExporter
from .mixins import PlanMixin


class PlanPdfExport(PlanMixin, DetailView):

    def render_to_response(self, context, *args, **kwargs):
        plan = context['plan']

        # Init response
        resp = HttpResponse(content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="Plan %s - RunReport.pdf"' % plan.name

        # Build pdf directly into response stream
        export = PlanPdfExporter(plan)
        export.render(resp)

        return resp


class PlanIcsExport(PlanMixin, DetailView):

    def render_to_response(self, context, *args, **kwargs):
        plan = context['plan']

        # Init response
        resp = HttpResponse(content_type='text/calendar')
        resp['Content-Disposition'] = 'attachment; filename="Plan %s - RunReport.ics"' % plan.name

        # Build ics calendar directly into response stream
        export = PlanIcsExporter(plan)
        export.build_calendar(resp)

        return resp
