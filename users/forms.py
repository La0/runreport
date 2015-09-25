from django import forms
from users.models import Athlete
from django.core.exceptions import ValidationError
from runreport.settings import GPG_HOME, GPG_KEY
from helpers import nameize
import gnupg
from tracks.providers.garmin import GarminProvider, GarminAuthException
from django.utils.translation import ugettext_lazy as _
from datetime import date

class DateSelectorWidget(forms.widgets.MultiWidget):
    '''
    Multiple select inputs to build a date
    From https://docs.djangoproject.com/en/1.8/ref/forms/widgets/
    '''
    def __init__(self, attrs=None):
        year = date.today().year
        years = [(y, y) for y in range(1900, year + 1)]
        years.reverse()
        months = [(m, m) for m in range(1,13)]
        days = [(d, d) for d in range(1, 32)]
        _widgets = (
            forms.widgets.Select(attrs=attrs, choices=days),
            forms.widgets.Select(attrs=attrs, choices=months),
            forms.widgets.Select(attrs=attrs, choices=years),
        )
        super(DateSelectorWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        print value
        if value:
            return [value.day, value.month, value.year]
        return [None, None, None]

    def format_output(self, rendered_widgets):
        return ''.join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        datelist = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)]
        try:
            D = date(
                day=int(datelist[0]),
                month=int(datelist[1]),
                year=int(datelist[2]),
            )
        except ValueError:
            return ''
        else:
            return D


class UserForm(forms.ModelForm):
  class Meta:
    model = Athlete
    fields = ('first_name', 'last_name', 'email', 'birthday', 'vma', 'frequency', 'frequency_rest', 'height', 'weight', 'comment', 'license', 'auto_send', 'nb_sessions', 'default_sport', 'avatar', 'privacy_avatar', 'privacy_records', 'privacy_races', 'privacy_stats', 'privacy_calendar', 'privacy_comments', 'privacy_tracks', 'language', 'daily_trainer_mail', 'display_help', 'phone', )
    widgets = {
      'nb_sessions' : forms.Select(choices=[(i,i) for i in range(0,21)]),
      'birthday' : DateSelectorWidget(),
    }

  def clean_email(self):
    email = self.cleaned_data['email']

    # Update mailing list subscriptions
    if self.instance and self.instance.email != email:
      mailings = ('all', )
      for m in mailings:
        try:
          self.instance.unsubscribe_mailing(m)
          self.instance.subscribe_mailing(m, email=email)
        except Exception:
          continue

    return email

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
  firstname = forms.CharField(label=_('Firstname'))
  lastname = forms.CharField(label=_('Lastname'))
  password = forms.CharField(min_length=4, widget=forms.PasswordInput(), label=_('Password'))
  password_check = forms.CharField(min_length=4, widget=forms.PasswordInput(), label=_('Repeat your password'))
  birthday = forms.DateField(label=_('Birthday'), widget=DateSelectorWidget())
  email = forms.EmailField(label=_('Email'))

  def __init__(self, invite=None, *args, **kwargs):
    self.invite = invite
    return super(SignUpForm, self).__init__(*args, **kwargs)

  def clean_firstname(self):
    return self.cleaned_data['firstname'].title()

  def clean_lastname(self):
    return self.cleaned_data['lastname'].title()

  def clean_email(self):
    '''
    Check email is unique
    '''
    # Skip on join invite
    if self.invite and self.invite.type == 'join':
      return self.cleaned_data['email']

    users = Athlete.objects.filter(email=self.cleaned_data['email'])
    if len(users) > 0:
      raise ValidationError(_('An account already uses this email.'))
    return self.cleaned_data['email']

  def clean_birthday(self):
    '''
    Check user is at least 13 years old
    '''
    bday = self.cleaned_data['birthday']
    diff = date.today() - bday
    if diff.days < 13 * 365:
      raise forms.ValidationError(_('You must be at least 13 years old to create an account.'))

    return bday

  def clean(self):
    '''
    Check passwords match
    '''
    if 'password' in self.cleaned_data and 'password_check' in self.cleaned_data:
      if self.cleaned_data['password'] != self.cleaned_data['password_check']:
        raise ValidationError(_('Please repeat the same password'))

    # Skip on join invite
    if self.invite and self.invite.type == 'join':
      return self.cleaned_data

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
  clear_password = ''
  user = None

  class Meta:
    model = Athlete
    fields = ('garmin_login', 'garmin_password')
    widgets = {
      'garmin_password' : forms.PasswordInput()
    }

  def __init__(self, user, *args, **kwargs):
    super(GarminForm, self).__init__(*args, **kwargs)
    self.user = user

  def clean_garmin_password(self):

    # Encrypt password
    self.clear_password = self.cleaned_data['garmin_password']
    gpg = gnupg.GPG(gnupghome=GPG_HOME)
    password = str(gpg.encrypt(self.clear_password, GPG_KEY))
    if not password:
      raise ValidationError("Failed to encrypt password")

    return password

  def clean(self):
    # Check login/password are valid
    try:
      provider = GarminProvider(self.user)
      provider.auth(force_login=self.cleaned_data['garmin_login'], force_password=self.clear_password)
    except GarminAuthException, e:
      print 'Garmin Auth failed : %s' % (str(e),)
      raise ValidationError(_('Invalid Garmin authentification'))

    return self.cleaned_data
