from users.models import Athlete
from django.views.generic.edit import FormView
from users.forms import SignUpForm
from django.contrib.auth import login as auth_login, authenticate
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class CreateUser(FormView):
  template_name = 'users/create.html'
  form_class = SignUpForm

  def form_valid(self, form):
    # Create user
    user = Athlete.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
    user.first_name = form.cleaned_data['firstname']
    user.last_name = form.cleaned_data['lastname']
    user.save()

    # Auto login
    valid_user = authenticate(username=user.username, password=form.cleaned_data['password'])
    if valid_user is not None:
      auth_login(self.request, valid_user)
    return HttpResponseRedirect(reverse('club-list'))
