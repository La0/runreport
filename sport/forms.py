#- coding: utf-8
from models import Sport, SportWeek, SportDay, SportSession, SESSION_TYPES
from datetime import date
from django import forms
from django.forms.models import BaseFormSet, inlineformset_factory

TIME_FORMATS = [
  '%H:%M:%S',
  '%H:%M',
  '%Hh%M',
  '%Hh %M',
  '%Hh %Mm %Ss',
  '%Mmin %Ss',
  '%Mmin',
]

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
    super(SportSessionForm, self).__init__(*args, **kwargs)

    multi_sports = False
    if hasattr(self, 'instance') and self.instance.pk:
      # Load multi sports from instance
      multi_sports = self.instance.day.week.user.multi_sports

    elif 'initial' in kwargs and 'multi_sports' in kwargs['initial']:
      # Load multi sports from initial data
      multi_sports = kwargs['initial']['multi_sports']

    self.sports = []
    if multi_sports:
      # Load only sports of depth 1 for this form
      self.sports = Sport.objects.filter(depth=1)
      self.fields['sport'].queryset = self.sports
    else:
      # No sport choice when multi_sports is disabled
      del self.fields['sport']

    # Apply default sport to instance
    if not hasattr(self.instance, 'sport') and 'sport' in self.initial:
      self.instance.sport = self.initial['sport']

  def clean(self, *args, **kwargs):
    super(SportSessionForm, self).clean(*args, **kwargs)

    if 'distance' in self.cleaned_data and self.cleaned_data['distance'] is None \
      and 'time' in self.cleaned_data and self.cleaned_data['time'] is None:
      raise forms.ValidationError('Spécifiez une distance ou un temps pour ajouter un sport.')

    return self.cleaned_data


class SportWeekForm(forms.ModelForm):
  class Meta:
    model = SportWeek
    fields = ('comment', )

class SportDayForm(forms.ModelForm):
  nb_extras = 4

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

    # Build formset with datas
    self.init_formset(data)

  def has_errors(self):
    '''
    Used by week view to detect if a redirect
    on valid action is possible to lose POST
    and not insert same sessions over and over
    on reload.
    '''
    if self.errors:
      return True
    return len([s for s in self.sessions if s.errors]) > 0


  def init_formset(self, data=None):
    # FormSet initial datas
    multi_sports = self.week.user.multi_sports
    initial = {
      'sport' : self.week.user.default_sport,
      'multi_sports' : multi_sports,
    }
    if not multi_sports:
      self.nb_extras = 1

    # Create FormSet from factory
    SportSessionFormSet = inlineformset_factory(SportDay, SportSession, extra=self.nb_extras, form=SportSessionForm)

    # Instanciate formset
    self.sessions = SportSessionFormSet(data, instance=self.instance, prefix=self.prefix, initial=[initial for i in range(self.nb_extras)])

  def clean(self):
    super(SportDayForm, self).clean()

    # Alert user about missing comment & name
    # Only when adding a sport session
    self.sessions.clean()
    if len([s for s in self.sessions if s.cleaned_data]):
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

    if not self.sessions.is_valid():
      return False

    # No error displayed for empty days
    return self.cleaned_data['name'] or self.cleaned_data['comment']

  def save(self, *args, **kwargs):
    # Save day
    day = super(SportDayForm, self).save(commit=False, *args, **kwargs)
    if self.week:
      day.week = self.week
    if self.date:
      day.date = self.date
    day.save()

    # Save sessions from formset
    for s in self.sessions.save(commit=False):
      s.day = day
      s.save()

    # Reset empty formset
    self.init_formset()

    return day

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
