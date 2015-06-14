from users.models import Athlete
from django.views.generic.edit import FormView
from users.forms import SignUpForm
from users.tasks import subscribe_mailing
from django.contrib.auth import login as auth_login, authenticate
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from .mixins import UserInviteMixin
from datetime import datetime

class CreateUser(UserInviteMixin, FormView):
  template_name = 'users/create.html'
  form_class = SignUpForm

  def get_context_data(self, *args, **kwargs):
    context = super(CreateUser, self).get_context_data(*args, **kwargs)

    # Use invite recipient data by default
    if self.invite:
      context['form'].fields['email'].initial = self.invite.recipient
      context['form'].fields['lastname'].initial = self.invite.name

    return context

  def form_valid(self, form):
    # Create user
    user = Athlete.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'], last_login=datetime.now())
    user.first_name = form.cleaned_data['firstname']
    user.last_name = form.cleaned_data['lastname']
    user.build_avatar()
    user.save()

    # Auto login
    valid_user = authenticate(email=user.email, password=form.cleaned_data['password'])
    if valid_user is not None:
      auth_login(self.request, valid_user)

    # When an invite is used, redirect to club creation
    # Otherwise, display club list
    url_name = self.invite and 'club-create' or 'club-list'

    # Subscribe user to mailing all
    subscribe_mailing.delay(user, 'all')

    return HttpResponseRedirect(reverse(url_name))

class ActivateUser(UserInviteMixin, FormView):
  template_name = 'users/create.html'
  form_class = SignUpForm

  def get_form_kwargs(self):
    # Add invite to kwargs
    kwargs = super(ActivateUser, self).get_form_kwargs()
    kwargs['invite'] = self.invite
    return kwargs

  def get_initial(self):
    if not self.invite and self.invite.type == 'join':
      raise Http404('No invite found.')

    return {
      'email' : self.invite.user.email,
      'firstname' : self.invite.user.first_name,
      'lastname' : self.invite.user.last_name,
    }

  def get_success_url(self):
    return reverse('report-current')

  def form_valid(self, form):
    if not self.invite and self.invite.type == 'join':
      raise Http404('No invite found.')

    user = self.invite.user

    # Update user from form data
    user.email = form.cleaned_data['email']
    user.first_name = form.cleaned_data['firstname']
    user.last_name= form.cleaned_data['lastname']
    user.set_password(form.cleaned_data['password'])
    user.save()

    # Auto login
    valid_user = authenticate(email=user.email, password=form.cleaned_data['password'])
    if valid_user is not None:
      auth_login(self.request, valid_user)

    # Subscribe user to mailing all
    subscribe_mailing.delay(user, 'all')

    # Mark invite as used
    self.invite.use()

    return super(ActivateUser, self).form_valid(form)
