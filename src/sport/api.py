from rest_framework.generics import RetrieveAPIView, ListAPIView
from users.models import Athlete
from django.shortcuts import get_object_or_404
from sport.models import Sport
from sport.serializers import StatsSerializer, SportSerializer
from sport.stats import SportStats


class UserAPIMixin(object):
    """
    Load user from url kwargs
    """
    def get_user(self):

        user = get_object_or_404(Athlete, username=self.kwargs['username'])

        # TODO: check rights

        return user


    def get_object(self):
        # Default object is asked user
        return self.get_user()


class SportList(ListAPIView):
    """
    List all available sports
    """
    serializer_class = SportSerializer
    queryset = Sport.objects.filter(depth__gte=1).order_by('depth', 'name')


class StatsView(UserAPIMixin, RetrieveAPIView):
    """
    Build stats for a user
    """
    serializer_class = StatsSerializer

    def get_object(self):
        """
        Calc stats on user instance
        and store results on local serializer instance
        """
        print(self.kwargs)
        return SportStats(
            user=self.get_user(),
            year=self.kwargs.get('year'),
            use_all_sessions=self.kwargs.get('all'),
        )
