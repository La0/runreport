from django import forms
from gear.models import GearItem
from sport.models import Sport


class GearItemForm(forms.ModelForm):
  '''
  Form to edit or create a GearItem
  '''
  def __init__(self, *args, **kwargs):
    super(GearItemForm, self).__init__(*args, **kwargs)

    # Sports are using checkbox
    # Limit sports to level 1
    self.fields['sports'].widget = forms.CheckboxSelectMultiple()
    self.fields['sports'].queryset = Sport.objects.filter(depth=1)


  class Meta:
    model = GearItem
    fields = ('name', 'description', 'brand', 'category', 'sports', 'start', 'end')
