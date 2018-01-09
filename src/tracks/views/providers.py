from django.views.generic import TemplateView
from django.views.generic.edit import DeletionMixin
from tracks.providers import all_providers, get_provider
from runreport.mixins import JsonResponseMixin, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE
from django.http import Http404


class TrackProviders(TemplateView):
    template_name = 'tracks/providers.html'

    def get_context_data(self, *args, **kwargs):
        context = super(TrackProviders, self).get_context_data(*args, **kwargs)
        context['providers'] = all_providers(self.request.user)
        return context


class TrackProviderDisconnect(JsonResponseMixin, DeletionMixin, TemplateView):
    template_name = 'tracks/disconnect.html'

    def get_provider(self):
        self.provider = get_provider(self.kwargs['name'], self.request.user)
        if not self.provider.is_connected():
            raise Http404('Not connected')

        return self.provider

    def get_context_data(self, *args, **kwargs):
        context = super(
            TrackProviderDisconnect,
            self).get_context_data(
            *args,
            **kwargs)
        context['provider'] = self.get_provider()
        return context

    def delete(self, *args, **kwargs):
        # Disconnect provider
        self.get_provider()
        self.provider.disconnect()

        # Reload providers page
        self.json_options = [
            JSON_OPTION_BODY_RELOAD,
            JSON_OPTION_NO_HTML,
            JSON_OPTION_CLOSE,
        ]
        return self.render_to_response({})
