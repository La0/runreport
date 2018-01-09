# encoding:utf-8
from django import forms
from users.models import Athlete
from django.forms.formsets import formset_factory
from django.core.exceptions import ValidationError
from club.models import ClubMembership, Club, ClubInvite, ClubLink, ClubGroup
from django.utils.translation import ugettext_lazy as _


class ClubMemberRoleForm(forms.ModelForm):
    # Add a boolean to cancel mail sending
    # When changing a role
    send_mail = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = ClubMembership
        fields = ('role', )
        widgers = {
            'role': forms.HiddenInput(),
        }


class ClubMemberTrainersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClubMemberTrainersForm, self).__init__(*args, **kwargs)

        # Load only trainers from instance club
        trainers = Athlete.objects.filter(
            memberships__club=self.instance.club,
            memberships__role='trainer')
        self.fields['trainers'] = UserModelChoiceField(
            queryset=trainers, widget=forms.CheckboxSelectMultiple(), required=False)

    class Meta:
        model = ClubMembership
        fields = ('trainers', )


class UserModelChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        try:
            if obj.first_name and obj.last_name:
                return '%s %s' % (obj.first_name, obj.last_name)
            return obj.first_name and obj.first_name or obj.username
        except BaseException:
            return '-'


class ClubCreateForm(forms.ModelForm):
    phone = forms.CharField(required=True, label=_('Phone'))

    # Setup countries dict
    from django_countries import Countries
    countries = [(k, v) for k, v in Countries().countries.items()]
    countries.sort(key=lambda x: x[1])

    manager_country = forms.ChoiceField(
        choices=countries,
        required=True,
        label=_('Your country of residence'))
    manager_nationality = forms.ChoiceField(
        choices=countries, required=True, label=_('Your nationality'))

    class Meta:
        model = Club
        fields = ('name', 'slug', 'address', 'zipcode', 'city', 'country', )

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


class ClubLinkForm(forms.ModelForm):
    class Meta:
        model = ClubLink
        fields = ('name', 'url')


class InviteAskForm(forms.ModelForm):
    class Meta:
        model = ClubInvite
        fields = ('recipient', )
        widgets = {
            'recipient': forms.TextInput(attrs={'placeholder': 'Votre email', }),
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
            raise forms.ValidationError(
                _('A group with this slug already exists.'))
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
                raise forms.ValidationError(
                    _('The CSV file has not 3 columns.'))

        return csv_source


class CSVAthleteForm(forms.Form):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)


CSVAthleteFormset = formset_factory(CSVAthleteForm)


class ClubInviteForm(forms.Form):
    '''
    Invite one athlete
    Smarter form thant the csv one above
    Add some checks
    '''
    email = forms.EmailField(required=True, label=_('Email'))
    first_name = forms.CharField(required=True, label=_('Firstname'))
    last_name = forms.CharField(required=True, label=_('Lastname'))

    def __init__(self, club, *args, **kwargs):
        super(ClubInviteForm, self).__init__(*args, **kwargs)
        self.club = club

    def clean(self):
        if self.club.invites.filter(
                recipient=self.cleaned_data['email']).exists():
            raise forms.ValidationError(_('This athlete is already invited.'))
