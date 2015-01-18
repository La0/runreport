from rest_framework import serializers
from users.models import Athlete
from plan.models import Plan, PlanSession

class AthleteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Athlete
    fields = ('pk', 'first_name', 'last_name', )

class PlanSessionSerializer(serializers.ModelSerializer):
  class Meta:
    model = PlanSession
    fields = ('pk', 'week', 'day', 'name', )

class PlanSerializer(serializers.ModelSerializer):
  sessions = PlanSessionSerializer(many=True)
  weeks_nb = serializers.IntegerField(source='get_weeks_nb', read_only=True)

  class Meta:
    model = Plan
    fields = ('pk', 'name', 'sessions', 'weeks_nb', )

  def create(self, validated_data):
    # Attach current user to plan creation
    plan = Plan(
      name=validated_data['name'],
      creator=self.context['request'].user,
    )
    plan.save()
    return plan
