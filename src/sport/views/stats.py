from django.views.generic import TemplateView



class SportStats(TemplateView):
    template_name = 'sport/stats.html'

    def get_url_context(self):
        # Gives user direct stats context
        return {
            'url_base': 'stats',
            'url_month': 'report-month',
            'url_args': [],
        }

    def get_context_data(self, *args, **kwargs):
        context = super(SportStats, self).get_context_data(*args, **kwargs)
        context.update(self.get_url_context())
        return context
