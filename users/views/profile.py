from users.forms import ProfileForm, UserForm, UserPasswordForm
from club.forms import TrainersFormSet
from coach.mixins import MultipleFormsView
from django.views.generic.edit import ModelFormMixin, FormView

class Profile(MultipleFormsView):
  template_name = 'users/profile.html'
  form_mask = 'form_trainers_%d'
  form_classes = {
    'form_user' : UserForm,
    'form_profile' : ProfileForm,
  }
  
  def get_forms(self, form_classes):
    forms = super(Profile, self).get_forms(form_classes)

    # Add manually formset for trainers
    kwargs = super(ModelFormMixin, self).get_form_kwargs()
    forms['form_trainers'] = TrainersFormSet(queryset=self.request.user.memberships.filter(role__in=('athlete', )), **kwargs)

    return forms

  def get_instance(self, key):
    instances = {
      'form_user' : self.request.user,
      'form_profile' : self.request.user.get_profile(),
    }
    return instances.get(key, None)

  def forms_valid(self, forms):
    forms['form_user'].save()
    forms['form_trainers'].save()

    # Search user category
    profile = forms['form_profile'].save(commit=False)
    profile.search_category()
    profile.save()

    return self.render_to_response(self.get_context_data(forms=forms))

  def get_context_data(self, **kwargs):
    context = super(Profile, self).get_context_data(**kwargs)
    for k,v in context['forms'].items():
      context[k] = v
    context['profile'] = self.request.user.get_profile()
    return context

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
