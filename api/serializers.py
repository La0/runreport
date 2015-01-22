from rest_framework import serializers
from users.models import Athlete
from sport.models import Sport
from plan.models import Plan, PlanSession

class AthleteSerializer(serializers.ModelSerializer):
  avatar = serializers.SerializerMethodField('get_avatar_url')

  class Meta:
    model = Athlete
    fields = ('id', 'first_name', 'last_name', 'avatar', )

  def get_avatar_url(self, athlete):
    '''
    Build avatar's absolute url
    '''
    return self.context['request'].build_absolute_uri(athlete.avatar.url)

class SportSerializer(serializers.ModelSerializer):
  class Meta:
    model = Sport
    fields = ('id', 'name', 'slug')

class PlanSessionSerializer(serializers.ModelSerializer):
  sport = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.filter(depth=1))

  class Meta:
    model = PlanSession
    fields = ('id', 'week', 'day', 'name', 'sport', 'type')

  def create(self, validated_data):
    # Attach plan to created session
    return PlanSession.objects.create(
      plan=self.context['view'].get_plan(),
      **validated_data
    )

class PlanSerializer(serializers.ModelSerializer):
  weeks_nb = serializers.IntegerField(source='get_weeks_nb', read_only=True)

  class Meta:
    model = Plan
    fields = ('id', 'name', 'weeks_nb', 'updated', 'start', )

  def create(self, validated_data):
    # Attach current user to plan creation
    plan = Plan(
      creator=self.context['request'].user,
      **validated_data
    )
    plan.save()
    return plan
