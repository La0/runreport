from django.middleware.csrf import CsrfViewMiddleware, _sanitize_token, _get_new_csrf_key, REASON_NO_REFERER, REASON_NO_CSRF_COOKIE, REASON_BAD_TOKEN, REASON_BAD_REFERER
from django.conf import settings
import logging
from django.utils.encoding import force_text
from django.utils.http import same_origin
from django.utils.crypto import constant_time_compare


logger = logging.getLogger('django.request')


class SubDomainCSRFMiddleware(CsrfViewMiddleware):
    '''
    Django checks that HTTPS POST/PUT/DELETE/... requests
    have a csrf token on *exactly* the same domain as
    the server it runs on.
    That does not work for legitimate requests from subdomains
    '''

    def process_view(self, request, callback, callback_args, callback_kwargs):

        if getattr(request, 'csrf_processing_done', False):
            return None

        try:
            csrf_token = _sanitize_token(
                request.COOKIES[settings.CSRF_COOKIE_NAME])
            # Use same token next time
            request.META['CSRF_COOKIE'] = csrf_token
        except KeyError:
            csrf_token = None
            # Generate token and store it in the request, so it's
            # available to the view.
            request.META["CSRF_COOKIE"] = _get_new_csrf_key()

        # Wait until request.META["CSRF_COOKIE"] has been manipulated before
        # bailing out, so that get_token still works
        # RunReport mod: No csrf_exempt needed (fails on DRF)
        #if getattr(callback, 'csrf_exempt', False):
        #    return None

        # Assume that anything not defined as 'safe' by RFC2616 needs protection
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if getattr(request, '_dont_enforce_csrf_checks', False):
                # Mechanism to turn off CSRF checks for test suite.
                # It comes after the creation of CSRF cookies, so that
                # everything else continues to work exactly the same
                # (e.g. cookies are sent, etc.), but before any
                # branches that call reject().
                return self._accept(request)

            if request.is_secure():
                # Suppose user visits http://example.com/
                # An active network attacker (man-in-the-middle, MITM) sends a
                # POST form that targets https://example.com/detonate-bomb/ and
                # submits it via JavaScript.
                #
                # The attacker will need to provide a CSRF cookie and token, but
                # that's no problem for a MITM and the session-independent
                # nonce we're using. So the MITM can circumvent the CSRF
                # protection. This is true for any HTTP connection, but anyone
                # using HTTPS expects better! For this reason, for
                # https://example.com/ we need additional protection that treats
                # http://example.com/ as completely untrusted. Under HTTPS,
                # Barth et al. found that the Referer header is missing for
                # same-domain requests in only about 0.2% of cases or less, so
                # we can use strict Referer checking.
                referer = force_text(
                    request.META.get('HTTP_REFERER'),
                    strings_only=True,
                    errors='replace'
                )
                if referer is None:
                    return self._reject(request, REASON_NO_REFERER)

                # Note that request.get_host() includes the port.
                allowed_hosts = settings.ALLOWED_HOSTS + [request.get_host(), ]
                allowed = False
                for host in allowed_hosts:
                    good_referer = 'https://%s/' % host
                    if same_origin(referer, good_referer):
                        allowed = True
                        break

                if not allowed:
                    reason = REASON_BAD_REFERER % (referer, good_referer)
                    return self._reject(request, reason)

            if csrf_token is None:
                # No CSRF cookie. For POST requests, we insist on a CSRF cookie,
                # and in this way we can avoid all CSRF attacks, including login
                # CSRF.
                return self._reject(request, REASON_NO_CSRF_COOKIE)

            # Check non-cookie token for match.
            request_csrf_token = ""
            if request.method == "POST":
                try:
                    request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')
                except IOError:
                    # Handle a broken connection before we've completed reading
                    # the POST data. process_view shouldn't raise any
                    # exceptions, so we'll ignore and serve the user a 403
                    # (assuming they're still listening, which they probably
                    # aren't because of the error).
                    pass

            if request_csrf_token == "":
                # Fall back to X-CSRFToken, to make things easier for AJAX,
                # and possible for PUT/DELETE.
                request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

            if not constant_time_compare(request_csrf_token, csrf_token):
                return self._reject(request, REASON_BAD_TOKEN)

        return self._accept(request)

