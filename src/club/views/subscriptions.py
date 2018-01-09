from django.views.generic import FormView
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .mixins import ClubManagerMixin
from club.forms import CSVSubscriptionsForm, CSVAthleteFormset, ClubInviteForm
from club.tasks import subscribe_athlete
from runreport.mixins import JsonResponseMixin, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE
import tempfile
import csv
import os

CSV_DIR = os.path.join(settings.ROOT, 'tmp')
CSV_SUFFIX = '.subscriptions.csv'


class ClubSubscriptionsAdd(JsonResponseMixin, ClubManagerMixin, FormView):
    '''
    Build & Send invite to an athlete
    '''
    template_name = 'club/subscriptions/add.html'
    form_class = ClubInviteForm

    def get_form_kwargs(self, *args, **kwargs):
        ctx = super(
            ClubSubscriptionsAdd,
            self).get_form_kwargs(
            *
            args,
            **kwargs)
        ctx['club'] = self.club
        return ctx

    def form_valid(self, form):
        subscribe_athlete.apply(
            args=(
                self.club,
                form.cleaned_data['email'],
                form.cleaned_data['first_name'],
                form.cleaned_data['last_name']))

        # Reload parent page
        self.json_options = [
            JSON_OPTION_BODY_RELOAD,
            JSON_OPTION_NO_HTML,
            JSON_OPTION_CLOSE,
        ]
        return self.render_to_response({})


class ClubSubscriptionsUpload(ClubManagerMixin, FormView):
    template_name = 'club/subscriptions/upload.html'
    form_class = CSVSubscriptionsForm

    def form_valid(self, form):
        csv = form.cleaned_data['csv']

        if not os.path.exists(CSV_DIR):
            os.mkdir(CSV_DIR)

        # Dump the csv in a temp path
        prefix = '%d.' % self.request.user.pk
        fd, path = tempfile.mkstemp(
            dir=CSV_DIR, prefix=prefix, suffix=CSV_SUFFIX)
        for chunk in csv.chunks():
            os.write(fd, chunk)  # low level FD

        # Get unique name
        name = os.path.basename(path)
        self.name = name[len(prefix):-len(CSV_SUFFIX)]

        # Redirect to subscriptions editor
        return super(ClubSubscriptionsUpload, self).form_valid(form)

    def get_success_url(self):
        return reverse('club-subscriptions-editor',
                       args=(self.club.slug, self.name, ))


class ClubSubscriptionsEditor(ClubManagerMixin, FormView):
    template_name = 'club/subscriptions/editor.html'
    form_class = CSVAthleteFormset

    def get_success_url(self):
        return reverse('club-manage', args=(self.club.slug, ))

    def get_initial(self):
        '''
        Load CSV file specified in kwargs
        '''
        # Check file
        name = '%d.%s%s' % (self.request.user.pk,
                            self.kwargs['csv_name'], CSV_SUFFIX)
        self.path = os.path.join(CSV_DIR, name)
        if not os.path.exists(self.path):
            raise PermissionDenied

        # Read file
        users = []
        with open(self.path, 'r') as csv_source:
            reader = csv.reader(csv_source, delimiter=';')
            for line in reader:
                users.append({
                    'email': line[0],
                    'first_name': line[1],
                    'last_name': line[2],
                })

        return users

    def form_valid(self, formset):
        for user in formset:
            data = user.cleaned_data
            if 'email' not in data:
                continue  # Skip extras

            # Start subscriptions tasks
            subscribe_athlete.delay(self.club, **data)

        # Remove csv file
        os.remove(self.path)

        return super(ClubSubscriptionsEditor, self).form_valid(formset)
