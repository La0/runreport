from rest_framework import serializers
from users.models import Athlete
from sport.models import Sport
from plan.models import Plan, PlanSession, PlanApplied
from club.models import ClubMembership, Club, ClubGroup
from messages.models import Message
from events.models import Place

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

class MessageSerializer(serializers.ModelSerializer):
  class Meta:
    model = Message
    fields = ('id', 'message')

  def create(self, validated_data, *args, **kwargs):
    '''
    Create a new directly attached Message
    '''
    session = self.context['view'].load_session()
    validated_data.update({
      'conversation' : session.comments,
      'writer' : self.context['request'].user,
    })
    return Message.objects.create(**validated_data)

class PlanAppliedSerializer(serializers.ModelSerializer):

  class Meta:
    model = PlanApplied
    fields = ('id', 'user', 'status')

class PlanSessionSerializer(serializers.ModelSerializer):
  sport = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.filter(depth=1))

  class Meta:
    model = PlanSession
    fields = ('id', 'week', 'day', 'name', 'sport', 'type', 'distance', 'time', 'place', 'hour' )

  def create(self, validated_data):
    # Attach plan to created session
    return PlanSession.objects.create(
      plan=self.context['view'].get_plan(),
      **validated_data
    )

class PlanSerializer(serializers.ModelSerializer):
  weeks_nb = serializers.IntegerField(read_only=True)
  sessions_nb = serializers.IntegerField(source='sessions.count', read_only=True)
  export_pdf = serializers.HyperlinkedIdentityField(view_name='plan-export-pdf')
  applications_nb = serializers.IntegerField(source='applications.count', read_only=True)
  is_active = serializers.BooleanField(read_only=True)

  class Meta:
    model = Plan
    fields = ('id', 'name', 'weeks_nb', 'sessions_nb', 'updated', 'start', 'end', 'export_pdf', 'applications_nb', 'is_active', )

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

class PlaceSerializer(serializers.ModelSerializer):
  '''
  List all places in a club
  '''
  class Meta:
    model = Place
    fields = ('id', 'name', 'address', 'zipcode', 'city')

class ClubMembershipSerializer(serializers.ModelSerializer):
  '''
  List all details about a trainer membership:
   * the club
   * the groups in the club
   * his athletes
   * his places
  '''
  club = ClubSerializer()
  groups = ClubGroupSerializer(many=True, source='groups_owned')
  athletes = AthleteMembershipSerializer(many=True)
  places = PlaceSerializer(source='club.places', many=True)

  class Meta:
    model = ClubMembership
    fields = ('id', 'role', 'created', 'club', 'groups', 'athletes', 'places', )

