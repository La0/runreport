from rest_framework import serializers
from users.models import Athlete
from sport.models import Sport
from plan.models import Plan, PlanSession
from club.models import ClubMembership, Club, ClubGroup

class AthleteSerializer(serializers.ModelSerializer):
  avatar = serializers.SerializerMethodField('get_avatar_url')

  class Meta:
    model = Athlete
    fields = ('id', 'first_name', 'last_name', 'avatar', 'language',)

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
  export_pdf = serializers.HyperlinkedIdentityField(view_name='plan-export-pdf')

  class Meta:
    model = Plan
    fields = ('id', 'name', 'weeks_nb', 'updated', 'start', 'export_pdf', )

  def create(self, validated_data):
    # Attach current user to plan creation
    plan = Plan(
      creator=self.context['request'].user,
      **validated_data
    )
    plan.save()
    return plan

class ClubSerializer(serializers.ModelSerializer):

  class Meta:
    model = Club
    fields = ('id', 'name', 'slug')

class ClubGroupSerializer(serializers.ModelSerializer):
  members = serializers.IntegerField(source='nb_members')

  class Meta:
    model = ClubGroup
    fields = ('id', 'name', 'slug', 'description', 'members', )

class AthleteMembershipSerializer(serializers.ModelSerializer):
  user = AthleteSerializer()

  class Meta:
    model = ClubMembership
    fields = ('user', 'role', 'groups')

class ClubMembershipSerializer(serializers.ModelSerializer):
  '''
  List all details about a trainer membership:
   * the club
   * the groups in the club
   * his athletes
  '''
  club = ClubSerializer()
  groups = ClubGroupSerializer(many=True, source='groups_owned')
  athletes = AthleteMembershipSerializer(many=True)

  class Meta:
    model = ClubMembership
    fields = ('id', 'role', 'created', 'club', 'groups', 'athletes', )
