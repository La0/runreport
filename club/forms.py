from models import ClubMembership
from django import forms
from django.contrib.auth.models import User
from django.forms.models import modelformset_factory

class ClubMembershipForm(forms.ModelForm):
  class Meta:
    model = ClubMembership
    fields = ('role', )

class UserModelChoiceField(forms.ModelMultipleChoiceField):
  def label_from_instance(self, obj):
    try:
      return obj.first_name and obj.first_name or obj.username
    except:
      return '-'

class TrainersForm(forms.ModelForm):
  def __init__(self, *args,**kwargs):
    super (TrainersForm, self ).__init__(*args,**kwargs) # populates the post

    # Only load trainers for instance club
    trainers = User.objects.filter(memberships__club=self.instance.club, memberships__role='trainer')
    self.fields['trainers'] = UserModelChoiceField(queryset=trainers, widget=forms.CheckboxSelectMultiple())

  class Meta:
    model = ClubMembership
    fields = ('trainers', )

# Init the formset using above form
TrainersFormSet = modelformset_factory(ClubMembership, fields=('trainers',), form=TrainersForm, extra=0)
