from helpers import render
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from coach.settings import LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL
from django.contrib.auth import login as auth_login, logout as auth_logout

@render('users/login.html')
def login(request):
  '''
  Almost a copy from django.contrib.auth.views.login
  Needed to work with jinja2 temmplates
  '''
  if request.method == 'POST':
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
      auth_login(request, form.get_user())

      if request.session.test_cookie_worked():
          request.session.delete_test_cookie()

      return HttpResponseRedirect(LOGIN_REDIRECT_URL)
  else:
    form = AuthenticationForm(request)
  
  request.session.set_test_cookie()

  return {
    'form' : form,
  }


def logout(request):
  auth_logout(request)
  return HttpResponseRedirect(LOGOUT_REDIRECT_URL)
