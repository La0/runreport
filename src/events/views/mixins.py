from django.urls import reverse
from club.views.mixins import ClubMixin
from events.models import Place
from events.forms import PlaceForm


class PlaceClubMixin(ClubMixin):
    template_name = 'events/places/edit.html'
    context_object_name = 'place'
    model = Place
    form_class = PlaceForm

    def form_valid(self, form):
        # Add user & club
        place = form.save(commit=False)
        place.creator = self.request.user
        place.club = self.club

        # Try to geocode
        try:
            place.geocode()
        except Exception as e:
            print(
                'Geocoding place #%s failed : %s' %
                (place.pk or 'nopk', e.message))

        # Finally save
        place.save()

        return super(PlaceClubMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('places', args=(self.club.slug, ))
