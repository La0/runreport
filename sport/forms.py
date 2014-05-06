#- coding: utf-8
from models import Sport, SportWeek, SportDay, SportSession, SESSION_TYPES
from datetime import date
from django import forms

TIME_FORMATS = [
  '%H:%M:%S',
  '%H:%M',
  '%Hh%M',
  '%Hh %M',
  '%Hh %Mm %Ss',
  '%Mmin %Ss',
  '%Mmin',
]

class SportWeekForm(forms.ModelForm):
  class Meta:
    model = SportWeek
    fields = ('comment', )

class SportDayForm(forms.ModelForm):
  class Meta:
    model = SportDay
    fields = ('name', 'comment', 'type', 'race_category')
    widgets = {
      'type' : forms.HiddenInput(),
    }

  def __init__(self, data=None, week=None, date=None, *args, **kwargs):
    self.week = week
    self.date = date

    # Base init
    super(SportDayForm, self).__init__(data, *args, **kwargs)
    if not self.prefix:
      self.prefix = 'day'

    sessions = self.instance.sessions.all()
    if sessions:
      # Add sessions form
      self.sessions = [SportSessionForm(data, instance=s, prefix='%s-%d' % (self.prefix, s.pk)) for s in sessions]
    else:
      # Add a default sport session
      default_sport = Sport.objects.get(slug='running')
      session = SportSession(sport=default_sport)
      self.sessions = [SportSessionForm(data, instance=session, prefix='%s-default' % (self.prefix, )), ]

  def clean(self):
    # Only for race
    if self.cleaned_data['type'] == 'race':

      # Check time & distance are set, for past races
      #session_date = self.instance.date or self.prefix # Get the date even if not in db
      #if session_date <= date.today() and (self.cleaned_data.get('time', None) is None or self.cleaned_data.get('distance', None) is None):
      #  raise forms.ValidationError(u"Pour une course passée, renseignez la distance et le temps.")

      # Check race category
      if not self.cleaned_data['race_category']:
        raise forms.ValidationError(u"Sélectionnez un type de course.")

    return self.cleaned_data

  def is_valid(self):
    is_valid = super(SportDayForm, self).is_valid()
    if not is_valid:
      return False

    # Check sessions
    if False in [s.is_valid() for s in self.sessions]:
      return False

    # Don't save any empty sesion, but no message for user
    if not self.cleaned_data.get('name', None) and not self.cleaned_data.get('comment', None):
      return False

    return True

  def save(self, *args, **kwargs):
    # Save day
    day = super(SportDayForm, self).save(commit=False, *args, **kwargs)
    if self.week:
      day.week = self.week
    if self.date:
      day.date = self.date
    day.save()

    # Save sessions linked to day
    for session_form in self.sessions:
      session = session_form.save(commit=False)
      session.day = day
      session.save()

    return day

class SportSessionForm(forms.ModelForm):
  time = forms.TimeField(input_formats=TIME_FORMATS, widget=forms.TextInput(attrs={'placeholder':'hh:mm'}), required=False)
  distance = forms.FloatField(localize=True, widget=forms.TextInput(attrs={'placeholder': 'km'}), required=False)

  class Meta:
    model = SportSession
    fields = ('sport', 'distance', 'time')

  def __init__(self, *args, **kwargs):
    super(SportSessionForm, self).__init__(*args, **kwargs)

    # Load only sports of depth 1 for this form
    self.fields['sport'].queryset = Sport.objects.filter(depth=1)

class SportDayAddForm(forms.Form):
  '''
  Form to create manually a new empty session
  '''
  date = forms.DateField()
  type = forms.ChoiceField(required=False, choices=SESSION_TYPES)

  def __init__(self, user, *args, **kwargs):
    self.user = user
    super(SportDayAddForm, self).__init__(*args, **kwargs)

  def clean_date(self):

    # Check date is free
    if SportDay.objects.filter(report__user=self.user, date=self.cleaned_data['date']):
      raise forms.ValidationError('Une séance existe déjà à cette date.')

    return self.cleaned_data['date']
