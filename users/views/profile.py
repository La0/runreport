from users.forms import ProfileForm, UserForm
from club.forms import TrainersForm
from coach.mixins import MultipleFormsView

class Profile(MultipleFormsView):
  template_name = 'users/profile.html'
  form_mask = 'form_trainers_%d'
  form_classes = {
    'form_user' : UserForm,
    'form_profile' : ProfileForm,
  }
  
  def get_form_classes(self):
    self.members = self.request.user.memberships.all()
    for m in self.members:
      self.form_classes[self.form_mask % m.club.id] = TrainersForm
    return self.form_classes

  def get_instance(self, key):
    instances = {
      'form_user' : self.request.user,
      'form_profile' : self.request.user.get_profile()
    }
    for m in self.members:
      instances[self.form_mask % m.club.id] = m
    return instances.get(key, None)

  def get_form_kwargs(self, key):
    kwargs = super(MultipleFormsView, self).get_form_kwargs(key)
    mask = self.form_mask[:-2]
    if key.startswith(mask):
      kwargs['club'] = self.members.get(club__id=int(key[len(mask):])).club
    return kwargs

  def forms_valid(self, forms):
    forms['form_user'].save()
    forms['form_profile'].save()
    for m in self.members:
      forms[self.form_mask % m.club.id].save()
    return self.render_to_response(self.get_context_data(forms=forms))

  def get_context_data(self, **kwargs):
    context = super(Profile, self).get_context_data(**kwargs)
    for k,v in context['forms'].items():
      context[k] = v
    context['profile'] = self.request.user.get_profile()
    context['memberships'] = self.members
    return context
