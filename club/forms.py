from models import ClubMembership
from django import forms

class ClubMembershipForm(forms.ModelForm):
  class Meta:
    model = ClubMembership
    fields = ('role', )
