from django import forms
from users.models import Athlete
from django.core.exceptions import ValidationError
from coach.settings import GPG_HOME, GPG_KEY
from helpers import nameize
import gnupg
from run.garmin import GarminConnector

class UserForm(forms.ModelForm):
  class Meta:
    model = Athlete
    fields = ('first_name', 'last_name', 'email', 'birthday', 'vma', 'frequency', 'frequency_rest', 'height', 'weight', 'comment', 'license', 'auto_send', 'nb_sessions', )
    widgets = {
      'nb_sessions' : forms.Select(choices=[(i,i) for i in range(0,21)]),
    }

class UserPasswordForm(forms.Form):
  password_old = forms.CharField(widget=forms.PasswordInput())
  password_new = forms.CharField(widget=forms.PasswordInput())
  password_check = forms.CharField(widget=forms.PasswordInput())

  def __init__(self, user, *args, **kwargs):
    super(UserPasswordForm, self).__init__(*args, **kwargs)
    self.user = user

  def clean_password_old(self):
    if not self.user.check_password(self.cleaned_data['password_old']):
      raise ValidationError('Mot de passe actuel invalide.')
    return self.cleaned_data['password_old']

  def clean_password_check(self):
    if self.cleaned_data.get('password_new', 'a') != self.cleaned_data.get('password_check', 'b'):
      raise ValidationError('Verification invalide.')
    return self.cleaned_data

class SignUpForm(forms.Form):
  firstname = forms.CharField()
  lastname = forms.CharField()
  password = forms.CharField(min_length=4, widget=forms.PasswordInput())
  password_check = forms.CharField(min_length=4, widget=forms.PasswordInput())
  email = forms.EmailField()

  def clean_email(self):
    '''
    Check email is unique
    '''
    users = Athlete.objects.filter(email=self.cleaned_data['email'])
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
    if 'firstname' in self.cleaned_data and 'lastname' in self.cleaned_data:
      i = 2
      base_name = name = nameize('%(firstname)s %(lastname)s' % self.cleaned_data)
      while True:
        try:
          Athlete.objects.get(username=name)
          name = '%s_%d' % (base_name, i)
          i += 1
        except:
          break
      self.cleaned_data['username'] = name
    return self.cleaned_data

class GarminForm(forms.ModelForm):

  class Meta:
    model = Athlete
    fields = ('garmin_login', 'garmin_password')
    widgets = {
      'garmin_password' : forms.PasswordInput()
    }

  def clean_garmin_password(self):

    # Encrypt password
    gpg = gnupg.GPG(gnupghome=GPG_HOME)
    password = str(gpg.encrypt(self.cleaned_data['garmin_password'], GPG_KEY))
    if not password:
      raise ValidationError("Failed to encrypt password")

    return password

  def clean(self):
    # Check login/password are valid
    try:
      gc = GarminConnector(login=self.cleaned_data['garmin_login'], password=self.cleaned_data['garmin_password'])
      gc.login()
    except Exception, e:
      raise ValidationError(str(e))
    return self.cleaned_data
