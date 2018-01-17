from django.views.generic import View
from django.views.generic.edit import FormView
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from .mixins import UserInviteMixin


class LoginUser(UserInviteMixin, FormView):
    form_class = AuthenticationForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        '''
        Almost a copy from django.contrib.auth.views.login
        Needed to work with jinja2 temmplates
        '''
        auth_login(self.request, form.get_user())
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        # End session when browser is closed
        if 'remember' not in self.request.POST:
            self.request.session.set_expiry(0)

        if self.invite:
            # Redirect to club creation on invite
            next_url = reverse('club-create')
        else:
            # Classic redirection, precedence to ?next=
            next_url = self.request.GET.get('next', settings.LOGIN_REDIRECT_URL)

        return HttpResponseRedirect(next_url)


class LogoutUser(View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
