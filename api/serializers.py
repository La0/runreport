from rest_framework import serializers
from users.models import Athlete
from plan.models import Plan

class AthleteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Athlete
    fields = ('pk', 'first_name', 'last_name', )

class PlanSerializer(serializers.ModelSerializer):
  class Meta:
    model = Plan
    fields = ('pk', 'name', )

  def create(self, validated_data):
    # Attach current user to plan creation
    plan = Plan(
      name=validated_data['name'],
      creator=self.context['request'].user,
    )
    plan.save()
    return plan
