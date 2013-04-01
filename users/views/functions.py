from helpers import render
from django.contrib.auth.decorators import login_required
from users.forms import ProfileForm, UserForm

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

