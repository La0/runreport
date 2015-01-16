from rest_framework import serializers
from users.models import Athlete

class AthleteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Athlete
    fields = ('pk', 'first_name', 'last_name', )

