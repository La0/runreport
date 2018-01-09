from django.views.generic import TemplateView
from tracks.providers import get_provider
from django.core.exceptions import PermissionDenied
from urlparse import parse_qs


class TrackOauthRedirect(TemplateView):
    template_name = 'tracks/oauth.html'

    def get_context_data(self, *args, **kwargs):
        context = super(
            TrackOauthRedirect,
            self).get_context_data(
            *
            args,
            **kwargs)

        context.update(self.check_provider())

        return context

    def check_provider(self):
        # Load provider
        provider = get_provider(self.kwargs['provider'], self.request.user)
        if not provider:
            raise PermissionDenied

        # Load query string
        args = parse_qs(self.request.META['QUERY_STRING'], strict_parsing=True)
        if not 'code' in args:
            raise PermissionDenied

        # Check state
        if 'state' in args and len(args['state']) == 1:
            # removed by parse_qs :(
            state = args['state'][0].replace(' ', '+')
            seed, _ = state.split('.')
            state_check = provider.build_user_state(int(seed))
            if state != state_check:
                raise PermissionDenied

        # Get access token
        error = None
        response = None
        try:
            response = provider.get_token(args['code'][0])
        except Exception as e:
            error = e

        return {
            'provider': provider.NAME,
            'auth_url': response is None and provider.auth() or None,
            'response': response,
            'error': error,
        }
