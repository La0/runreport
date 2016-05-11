from users.forms import UserForm, UserPasswordForm
from django.views.generic.edit import UpdateView, FormView
from users.models import Athlete
from users.tasks import update_ml_usage

class Preferences(UpdateView):
  template_name = 'users/preferences.html'
  form_class = UserForm
  model = Athlete
  old_email = None

  def get_object(self):
    if not self.old_email:
      self.old_email = self.request.user.email # Save here
    return self.request.user

  def form_valid(self, form):
    if self.request.user.demo:
      raise Exception('No edition for demo')

    # Cleanup previous avatar
    avatar_updated = False
    if form.cleaned_data['avatar'] and self.request.FILES:
      self.request.user.clean_avatars()
      avatar_updated = True

    # Update user category
    user = form.save(commit=False)
    user.search_category()
    user.save()

    # Crop updated avatar
    if avatar_updated:
      user.crop_avatar()

    # Update mailing list on email change
    new_email = form.cleaned_data['email']
    if self.old_email != new_email:
      update_ml_usage.delay(self.request.user, self.old_email, new_email)

    return self.render_to_response(self.get_context_data(form=form))

class UpdatePassword(FormView):
  template_name = 'users/password.html'

  def get_form(self, *args, **kwargs):
    if self.request.method == 'POST':
      return UserPasswordForm(self.request.user, data=self.request.POST)
    return UserPasswordForm(self.request.user)

  def form_valid(self, form):
    # Update password
    self.request.user.set_password(form.cleaned_data['password_new'])
    self.request.user.save()

    return self.render_to_response({'form' : None})

