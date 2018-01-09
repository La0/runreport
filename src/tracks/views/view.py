from django.views.generic.detail import BaseDetailView
from .mixins import TrackMixin
from runreport.mixins import JsonResponseMixin, JSON_OPTION_RAW, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML
from sport.models import SportSession


class TrackCoordsView(TrackMixin, JsonResponseMixin, BaseDetailView):
    json_options = [JSON_OPTION_RAW, ]

    def get_context_data(self, *args, **kwargs):
        track = self.object
        return {
            # Base informations
            'id': track.id,
            'provider': {
                'name': track.provider,
                'id': track.provider_id,
            },

            # Output the coordinates
            'coordinates': track.simple and track.simple.coords or [],
        }


class TrackSessionView(TrackMixin, JsonResponseMixin, BaseDetailView):
    json_options = [JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, ]

    def post(self, *args, **kwargs):

        # Check ownership on track
        track = self.get_object(check_ownership=True)

        # Load target session
        session = SportSession.objects.get(
            pk=self.request.POST['session'],
            day=track.session.day)

        # Update track's session
        track.session = session
        track.save()

        return super(TrackSessionView, self).render_to_response({})
