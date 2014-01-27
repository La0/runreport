from models import ClubMembership, Club, ClubInvite, ClubLink
from django import forms
from users.models import Athlete
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError

class ClubMembershipForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(ClubMembershipForm, self).__init__(*args, **kwargs)

    # Load only trainers from instance club
    trainers = Athlete.objects.filter(memberships__club=self.instance.club, memberships__role='trainer')
    self.fields['trainers'] = UserModelChoiceField(queryset=trainers, widget=forms.CheckboxSelectMultiple(), required=False)

  class Meta:
    model = ClubMembership
    fields = ('role', 'trainers', )

class UserModelChoiceField(forms.ModelMultipleChoiceField):
  def label_from_instance(self, obj):
    try:
      return obj.first_name and obj.first_name or obj.username
    except:
      return '-'

class ClubCreateForm(forms.ModelForm):
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
