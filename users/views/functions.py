from helpers import render
from django.http import HttpResponseRedirect
from django.db.models import Max
from django.contrib.auth.models import User, Group
from coach.settings import LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL, TRAINERS_GROUP
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from users.forms import ProfileForm, UserForm, SignUpForm, GarminForm
from run.models import GarminActivity

@login_required
@render('users/profile.html')
def profile(request):
  profile = request.user.get_profile()

  # Load trainers in form
  if request.method == 'POST':
    form_profile = ProfileForm(request.POST, instance=profile)
    form_user = UserForm(request.POST, instance=request.user)
    if form_profile.is_valid() and form_user.is_valid():
      form_profile.save()
      form_user.save()
  else:
    form_profile = ProfileForm(instance=profile)
    form_user = UserForm(instance=request.user)

  return {
    'profile' : profile,
    'form_profile' : form_profile,
    'form_user' : form_user,
  }

@login_required
@render('users/garmin.html')
def garmin(request):
  profile = request.user.get_profile()

  if request.method == 'POST':
    form = GarminForm(request.POST, instance=profile)
    if form.is_valid():
      form.save()
  else:
    form = GarminForm(instance=profile)

  # Imported Activities
  activities = GarminActivity.objects.filter(user=request.user)

  return {
    'form' : form,
    'activities_nb' : activities.count(),
    'activities_dates' : activities.aggregate(created=Max('created'), updated=Max('updated')),
  }
