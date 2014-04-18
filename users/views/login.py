from django.views.generic import View
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from coach.settings import LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL
from django.contrib.auth import login as auth_login, logout as auth_logout

class LoginUser(FormView):
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

    next_url = self.request.GET.get('next', LOGIN_REDIRECT_URL)
    return HttpResponseRedirect(next_url)

class LogoutUser(View):
  def get(self, request, *args, **kwargs):
    auth_logout(request)
    return HttpResponseRedirect(LOGOUT_REDIRECT_URL)
