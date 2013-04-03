from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from users.forms import ProfileForm, UserForm
from coach.mixins import MultipleFormsView

class Profile(MultipleFormsView):
  template_name = 'users/profile.html'
  form_classes = {
    'form_user' : UserForm,
    'form_profile' : ProfileForm,
  }

  def get_instance(self, key):
    instances = {
      'form_user' : self.request.user,
      'form_profile' : self.request.user.get_profile()
    }
    return instances.get(key, None)

  def forms_valid(self, forms):
    forms['form_user'].save()
    forms['form_profile'].save()
    return self.render_to_response(self.get_context_data(forms=forms))

  def get_context_data(self, **kwargs):
    context = super(Profile, self).get_context_data(**kwargs)
    context['form_user'] = context['forms']['form_user']
    context['form_profile'] = context['forms']['form_profile']
    context['profile'] = self.request.user.get_profile()
    return context
