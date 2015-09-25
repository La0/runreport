from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django import forms
from gear.models import GearItem, GearCategory, GearBrand
from sport.models import Sport


class GearItemForm(forms.ModelForm):
  '''
  Form to edit or create a GearItem
  '''
  new_category = forms.CharField(required=False, label=_('New category'))
  new_brand = forms.CharField(required=False, label=_('New brand'))

  class Meta:
    model = GearItem
    fields = ('name', 'description', 'brand', 'category', 'sports', 'start', 'end')
    widgets = {
        # Placeholders
        'new_category' : forms.TextInput(attrs={'placeholder' : _('Name of the new category')}),
        'new_brand' : forms.TextInput(attrs={'placeholder' : _('Name of the new brand')}),

        # Sports are using checkbox
        'sports' : forms.CheckboxSelectMultiple(),
    }

  def __init__(self, user, *args, **kwargs):
    super(GearItemForm, self).__init__(*args, **kwargs)

    # Save user
    self.user = user

    # Category & brand are not required
    self.fields['category'].required = False
    self.fields['brand'].required = False

    # Limit category & brand queryset
    filters = Q(owner=self.user) | Q(official=True)
    self.fields['category'].queryset = GearCategory.objects.filter(filters)
    self.fields['brand'].queryset = GearBrand.objects.filter(filters)

    # Limit sports to level 1
    self.fields['sports'].queryset = Sport.objects.filter(depth=1)

  def clean(self):
    def _check_moderated(name, cls):
      # Check we have model or new model
      if self.cleaned_data.get(name):
        return
      new_name = self.cleaned_data.get('new_%s' % name)
      if not new_name:
        raise forms.ValidationError(_('Empty category or brand'))

      # Build new name
      self.cleaned_data[name] = cls.objects.create(name=new_name, owner=self.user)

    _check_moderated('category', GearCategory)
    _check_moderated('brand', GearBrand)

    return self.cleaned_data
