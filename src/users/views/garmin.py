from django.views.generic.edit import UpdateView
from users.forms import GarminForm
from users.models import Athlete
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


class GarminLogin(UpdateView):
    template_name = 'users/garmin.html'
    form_class = GarminForm
    model = Athlete

    def get_form_kwargs(self, *args, **kwargs):
        fkw = super(GarminLogin, self).get_form_kwargs(*args, **kwargs)
        fkw['user'] = self.request.user
        return fkw

    def get_object(self):
        return self.request.user

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return HttpResponseRedirect(reverse('track-providers'))
