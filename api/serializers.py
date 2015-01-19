from rest_framework import serializers
from users.models import Athlete
from plan.models import Plan, PlanSession

class AthleteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Athlete
    fields = ('id', 'first_name', 'last_name', )

class PlanSessionSerializer(serializers.ModelSerializer):
  class Meta:
    model = PlanSession
    fields = ('id', 'week', 'day', 'name', )

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
    fields = ('id', 'name', 'weeks_nb', )

  def create(self, validated_data):
    # Attach current user to plan creation
    plan = Plan(
      name=validated_data['name'],
      creator=self.context['request'].user,
    )
    plan.save()
    return plan
