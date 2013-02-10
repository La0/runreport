from django import forms
from models import UserProfile
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from coach.settings import TRAINERS_GROUP
from helpers import nameize

class ProfileForm(forms.ModelForm):
  class Meta:
    model = UserProfile
    exclude = ('user', )

class UserForm(forms.Form):
  firstname = forms.CharField()
  lastname = forms.CharField()
  password = forms.CharField(min_length=4, widget=forms.PasswordInput())
  password_check = forms.CharField(min_length=4, widget=forms.PasswordInput())
  email = forms.EmailField()
  trainer = forms.ModelChoiceField(queryset=User.objects.filter(groups=TRAINERS_GROUP))

  def clean_email(self):
    '''
    Check email is unique
    '''
    users = User.objects.filter(email=self.cleaned_data['email'])
    if len(users) > 0:
      raise ValidationError('Un compte existe deja avec cet email.')
    return self.cleaned_data['email']

  def clean(self):
    '''
    Check passwords match
    '''
    if 'password' in self.cleaned_data and 'password_check' in self.cleaned_data:
      if self.cleaned_data['password'] != self.cleaned_data['password_check']:
        raise ValidationError('Entrez deux fois le meme mot de passe.')

    # Add unique username
    i = 2
    base_name = name = nameize('%(firstname)s %(lastname)s' % self.cleaned_data)
    while True:
      try:
        User.objects.get(username=name)
        name = '%s_%d' % (base_name, i)
        i += 1
      except:
        break
    self.cleaned_data['username'] = name
    return self.cleaned_data
