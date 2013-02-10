from helpers import render
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from coach.settings import LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL, TRAINERS_GROUP
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from forms import ProfileForm, UserForm

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

@login_required
@render('users/profile.html')
def profile(request):
  profile = request.user.get_profile()

  # Load trainers in form
  trainers = Group.objects.get(pk=TRAINERS_GROUP).user_set.all()
  if request.method == 'POST':
    form = ProfileForm(request.POST, instance=profile)
    form.fields['trainer'].queryset = trainers
    if form.is_valid():
      form.save()
  else:
    form = ProfileForm(instance=profile)
    form.fields['trainer'].queryset = trainers

  return {
    'profile' : profile,
    'form' : form,
  }

@render('users/create.html')
def create(request):
  if request.method == 'POST':
    form = UserForm(request.POST)
    if form.is_valid():

      # Create user & profile
      user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
      user.first_name = form.cleaned_data['firstname']
      user.last_name = form.cleaned_data['lastname']
      user.save()
      profile = user.get_profile()
      profile.trainer = form.cleaned_data['trainer']
      profile.save()

      # Auto login
      valid_user = authenticate(username=user.username, password=form.cleaned_data['password'])
      if valid_user is not None:
        auth_login(request, valid_user)
      return HttpResponseRedirect(LOGIN_REDIRECT_URL)
  else:
    form = UserForm()
  return {
    'form': form,
  }


def logout(request):
  auth_logout(request)
  return HttpResponseRedirect(LOGOUT_REDIRECT_URL)
