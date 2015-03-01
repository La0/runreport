from django.views.generic import FormView, TemplateView
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .mixins import ClubMixin
from club.forms import CSVSubscriptionsForm
import tempfile
import csv
import os

CSV_DIR = os.path.join(settings.HOME, 'tmp')
CSV_SUFFIX = '.subscriptions.csv'

class ClubSubscriptionsUpload(ClubMixin, FormView):
  template_name = 'club/subscriptions/upload.html'
  form_class = CSVSubscriptionsForm

  def form_valid(self, form):
    csv = form.cleaned_data['csv']

    if not os.path.exists(CSV_DIR):
      os.mkdir(CSV_DIR)

    # Dump the csv in a temp path
    prefix = '%d.' % self.request.user.pk
    fd, path = tempfile.mkstemp(dir=CSV_DIR, prefix=prefix, suffix=CSV_SUFFIX)
    for chunk in csv.chunks():
      os.write(fd, chunk) # low level FD

    # Get unique name
    name = os.path.basename(path)
    self.name = name[len(prefix):-len(CSV_SUFFIX)]

    # Redirect to subscriptions editor
    return super(ClubSubscriptionsUpload, self).form_valid(form)

  def get_success_url(self):
    return reverse('club-subscriptions-editor', args=(self.club.slug, self.name, ))

class ClubSubscriptionsEditor(ClubMixin, TemplateView):
  template_name = 'club/subscriptions/editor.html'

  def load_csv(self):
    '''
    Load CSV file specified in kwargs
    '''
    # Check file
    name = '%d.%s%s' % (self.request.user.pk, self.kwargs['csv_name'], CSV_SUFFIX)
    path = os.path.join(CSV_DIR, name)
    if not os.path.exists(path):
      raise PermissionDenied

    # Read file
    users = []
    with open(path, 'r') as csv_source:
      reader = csv.reader(csv_source, delimiter=';')
      for line in reader:
        users.append({
          'email' : line[0],
          'first_name' : line[1],
          'last_name' : line[2],
        })

    return {
      'users' : users,
    }

  def get_context_data(self, *args, **kwargs):
    context = super(ClubSubscriptionsEditor, self).get_context_data(*args, **kwargs)
    context.update(self.load_csv())
    return context
