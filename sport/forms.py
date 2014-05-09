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

    # Sessions init
    self.build_sessions(data)

  def build_sessions(self, data=None):
    '''
    Build all the SportSession forms
    '''
    default_sport = self.week.user.default_sport
    multi_sports = self.week.user.multi_sports
    sessions = self.instance.sessions.all()
    if sessions:
      # Add sessions form
      self.sessions = [SportSessionForm(data, instance=s, multi_sports=multi_sports, prefix='%s-%d' % (self.prefix, s.pk)) for s in sessions]

      # Add an empty extra session
      sports = [s.sport for s in sessions]
      if default_sport in sports:
        # Pick another sport
        sport = Sport.objects.exclude(sport__in=sports)[0]
      else:
        sport = default_sport

      # Build extra form, when multi sports is used
      if self.week.user.multi_sports:
        session = SportSession(sport=sport)
        extra_form = SportSessionForm(data, instance=session, prefix='%s-extra' % (self.prefix,))
        extra_form.extra = True # mark for templates
        self.sessions.append(extra_form)

    else:
      # Add a default sport session
      session = SportSession(sport=default_sport)
      self.sessions = [SportSessionForm(data, instance=session, multi_sports=multi_sports, prefix='%s-default' % (self.prefix, )), ]

  def clean(self):

    # Clean sessions
    sports = []
    for s in self.sessions:
      if s.is_valid():
        s.clean()

        # No duplicate sports ?
        if self.week.user.multi_sports:
          sport = s.cleaned_data['sport']
          if sport in sports:
            raise forms.ValidationError('Sport déja utilisé : %s' % sport)
          sports.append(sport)

        # Alert user about missing comment & name
        if not self.cleaned_data.get('name', None) and not self.cleaned_data.get('comment', None):
          raise forms.ValidationError(u'Vous devez spécifier un nom de séance et/ou un commentaire.')


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

    for session_form in self.sessions:
      if session_form.is_valid():
        # Save valid sessions linked to day
        session = session_form.save(commit=False)
        session.day = day
        session.save()
      elif session_form.instance.pk is not None:
        # Delete invalid sessions
        # Maybe a bad action here ?
        session_form.instance.delete()

    # Re-init sessions forms
    # to display new extra form
    self.build_sessions()

    return day

class SportSessionForm(forms.ModelForm):
  time = forms.TimeField(input_formats=TIME_FORMATS, widget=forms.TextInput(attrs={'placeholder':'hh:mm'}), required=False)
  distance = forms.FloatField(localize=True, widget=forms.TextInput(attrs={'placeholder': 'km'}), required=False)

  class Meta:
    model = SportSession
    fields = ('sport', 'distance', 'time')
    widgets = {
      'sport' : forms.HiddenInput(),
    }


  def __init__(self, *args, **kwargs):

    # Extract multi sports
    # otherwise it causes multiple args bug
    multi_sports = False
    if 'multi_sports' in kwargs:
      multi_sports = kwargs.pop('multi_sports')

    super(SportSessionForm, self).__init__(*args, **kwargs)

    self.sports = []
    if multi_sports:
      # Load only sports of depth 1 for this form
      self.sports = Sport.objects.filter(depth=1)
      self.fields['sport'].queryset = self.sports
    else:
      # No sport choice when multi_sports is disabled
      del self.fields['sport']
        

  def is_valid(self, *args, **kwargs):
    '''
    Valid only with time or distance specified
    '''
    is_valid = super(SportSessionForm, self).is_valid()
    if not is_valid:
      return False

    return self.cleaned_data['distance'] is not None or self.cleaned_data['time'] is not None

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
