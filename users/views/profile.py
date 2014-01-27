from users.forms import UserForm, UserPasswordForm
from club.forms import TrainersFormSet
from django.views.generic.edit import UpdateView, FormView
from users.models import Athlete

class Profile(UpdateView):
  template_name = 'users/profile.html'
  form_class = UserForm
  model = Athlete

  def get_object(self):
    return self.request.user

  def get_context_data(self, *args, **kwargs):
    context = super(Profile, self).get_context_data(*args, **kwargs)

    # Add form for trainers
    data = self.request.method == 'POST' and self.request.POST or None
    context['form_trainers'] = TrainersFormSet(data, queryset=self.request.user.memberships.filter(role__in=('athlete', )))

    return context

  def form_valid(self, form):
    context = self.get_context_data(form=form)

    # Update user category
    user = form.save(commit=False)
    user.search_category()
    user.save()

    # Manually save trainers form
    # This is really dirty.
    form = context['form_trainers']
    if form.is_valid():
      form.save()

    return self.render_to_response(context)

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
