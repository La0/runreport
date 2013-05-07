from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from users.forms import SignUpForm
from django.contrib.auth import login as auth_login, authenticate
from django.http import HttpResponseRedirect
from coach.settings import LOGIN_REDIRECT_URL
from club.models import ClubMembership

class CreateUser(FormView):
  template_name = 'users/create.html'
  form_class = SignUpForm

  def form_valid(self, form):
    # Create user
    user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
    user.first_name = form.cleaned_data['firstname']
    user.last_name = form.cleaned_data['lastname']
    user.save()

    # Add user to a club
    club = form.cleaned_data['club']
    print club
    cm = ClubMembership(user=user, club=club, role='athlete')
    cm.save()
    print cm.pk

    # Init profile
    profile = user.get_profile()
    profile.trainer = club.main_trainer
    profile.save()

    # Auto login
    valid_user = authenticate(username=user.username, password=form.cleaned_data['password'])
    if valid_user is not None:
      auth_login(self.request, valid_user)
    return HttpResponseRedirect(LOGIN_REDIRECT_URL)
