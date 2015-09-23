# encoding:utf-8
from models import ClubMembership, Club, ClubInvite, ClubLink
from django import forms
from users.models import Athlete
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory
from django.core.exceptions import ValidationError
from club.models import ClubGroup
from django.utils.translation import ugettext_lazy as _

class ClubMembershipForm(forms.ModelForm):
  # Add a boolean to cancel mail sending
  # When changing a role
  send_mail = forms.BooleanField(required=False, initial=True)

  def __init__(self, *args, **kwargs):
    super(ClubMembershipForm, self).__init__(*args, **kwargs)

    # Load only trainers from instance club
    trainers = Athlete.objects.filter(memberships__club=self.instance.club, memberships__role='trainer')
    self.fields['trainers'] = UserModelChoiceField(queryset=trainers, widget=forms.CheckboxSelectMultiple(), required=False)

    # Role is hidden
    self.fields['role'].widget = forms.HiddenInput()

  class Meta:
    model = ClubMembership
    fields = ('role', 'trainers', )

class UserModelChoiceField(forms.ModelMultipleChoiceField):
  def label_from_instance(self, obj):
    try:
      if obj.first_name and obj.last_name:
        return '%s %s' % (obj.first_name, obj.last_name)
      return obj.first_name and obj.first_name or obj.username
    except:
      return '-'

class ClubCreateForm(forms.ModelForm):
  phone = forms.CharField(required=True)

  class Meta:
    model = Club
    fields = ('name', 'slug', 'address', 'zipcode', 'city',)

  def clean_slug(self):
    # Check the slug is not already taken
    slug = self.cleaned_data['slug']
    existing = Club.objects.filter(slug=slug)
    if self.instance:
      existing = existing.exclude(pk=self.instance.pk)
    existing = existing.count()
    if existing > 0:
      raise ValidationError("Slug already used.")
    return slug

class TrainersForm(forms.ModelForm):
  def __init__(self, *args,**kwargs):
    super (TrainersForm, self ).__init__(*args,**kwargs) # populates the post

    # Only load trainers for instance club
    trainers = Athlete.objects.filter(memberships__club=self.instance.club, memberships__role='trainer')
    self.fields['trainers'] = UserModelChoiceField(queryset=trainers, widget=forms.CheckboxSelectMultiple())

  class Meta:
    model = ClubMembership
    fields = ('trainers', )

class ClubLinkForm(forms.ModelForm):
  class Meta:
    model = ClubLink
    fields = ('name', 'url')

# Init the formset using above form
TrainersFormSet = modelformset_factory(ClubMembership, fields=('trainers',), form=TrainersForm, extra=0)


class InviteAskForm(forms.ModelForm):
  class Meta:
    model = ClubInvite
    fields = ('recipient', )
    widgets = {
      'recipient' : forms.TextInput(attrs={'placeholder' : 'Votre email', }),
    }

  def clean_recipient(self):
    recipient = self.cleaned_data['recipient']
    if ClubInvite.objects.filter(recipient=recipient).exists():
      raise forms.ValidationError(u'Invitation déja demandée')

    return recipient


class ClubGroupForm(forms.ModelForm):
  class Meta:
    model = ClubGroup
    fields = ('name', 'slug', 'description')

  def __init__(self, club=None, *args, **kwargs):
    super(ClubGroupForm, self).__init__(*args, **kwargs)
    self.club = club

  def clean_slug(self):
    '''
    Check the slug is not already used
    '''
    slug = self.cleaned_data['slug']
    if self.club.groups.filter(slug=slug).exists():
      raise forms.ValidationError(_('A group with this slug already exists.'))
    return slug

class CSVSubscriptionsForm(forms.Form):
  csv = forms.FileField()

  def clean_csv(self):
    '''
    Check the csv has 3 columns
    '''
    import csv
    csv_source = self.cleaned_data['csv']
    reader = csv.reader(csv_source, delimiter=';')
    for line in reader:
      if len(line) != 3:
        raise forms.ValidationError(_('The CSV file has not 3 columns.'))

    return csv_source

class CSVAthleteForm(forms.Form):
  email = forms.EmailField(required=True)
  first_name = forms.CharField(required=True)
  last_name = forms.CharField(required=True)


CSVAthleteFormset = formset_factory(CSVAthleteForm)
