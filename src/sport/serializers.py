from rest_framework import serializers
from sport.models import Sport, SportDay, SportWeek, SportSession
from tracks.serializers import TrackSerializer
from datetime import date


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = (
            'id',
            'depth',
            'parent',
            'name',
            'slug',
        )


class StatsSerializer(serializers.Serializer):
    periods = serializers.SerializerMethodField()
    sports = serializers.SerializerMethodField()
    distances = serializers.SerializerMethodField()
    hours = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'periods',
            'sports',
            'distances',
            'hours',
        )

    def get_periods(self, stats):
        return stats.get_periods()

    def get_sports(self, stats):
        return stats.get_sports()

    def get_distances(self, stats):
        return stats.get_distances()

    def get_hours(self, stats):
        return stats.get_hours()


class SportSessionSerializer(serializers.ModelSerializer):
    '''
    Full serializer for a sport session
    '''
    sport = serializers.SlugRelatedField('slug', queryset=Sport.objects.filter(depth__gt=0))
    date = serializers.DateField(source='day.date')
    type = serializers.CharField(required=True)
    track = TrackSerializer(required=False)

    class Meta:
        model = SportSession
        fields = (
            'id',
            'day',
            'date',
            'name',
            'type',
            'race_category',
            'comment',
            'distance',
            'time',
            'sport',
            'note',
            'elevation_gain',
            'elevation_loss',
            'comments_public',
            'comments_private',
            'track',
            'created',
            'updated',
        )
        read_only_fields = (
            'day',
            'comments_public',
            'comments_private',
            'track',
        )

    def validate(self, data):

        # No check for rest session
        if data['type'] == 'rest':
            return data

        # Alert user about missing name
        if not data.get('name'):
            raise serializers.ValidationError('You must specify a name.', code='name')

        # Check we have time or distance for
        # * all trainings
        # * past sessions
        # * skip failed plans

        if (
            data['type'] == 'training' or
            (data['type'] == 'race' and data['day']['date'] <= date.today())
        ) \
                and data.get('plan_status') != 'failed' \
                and not data.get('distance') \
                and not data.get('time'):
            raise serializers.ValidationError(
                'You must specify a distance or time to add a session.',
                code='distance_time',
            )

        # Alert user about missing difficulty
        # For past sessions
        # Not on rest
        # Not on missed plan session
        if data['day']['date'] <= date.today() \
            and not data.get('note') \
            and data['type'] != 'rest' \
            and data.get('plan_status') in (None, '', 'applied', 'done', ):
            raise serializers.ValidationError(
                'You must specify a difficulty note.',
                code='note',
            )

        # Only for race
        if data['type'] == 'race':

            # Check race category
            if not data['race_category']:
                raise serializers.ValidationError('Pick a race category.', code='race_category')

        return data


class SportSessionLightSerializer(serializers.ModelSerializer):
    '''
    Light serializer for a sport session
    Used by calendars
    '''
    sport = serializers.SlugRelatedField('slug', read_only=True)

    class Meta:
        model = SportSession
        fields = (
            'id',
            'name',
            'type',
            'sport',
            'note',
        )

class SportDaySerializer(serializers.ModelSerializer):
    # Only showcases light infos on calendar
    sessions = SportSessionLightSerializer(many=True)

    class Meta:
        model = SportDay
        fields = (
            'id',
            'date',
            'sessions',
        )

class SportWeekSerializer(serializers.ModelSerializer):
    days = SportDaySerializer(many=True)

    class Meta:
        model = SportWeek
        fields = (
            'id',
            'published',
            'created',
            'updated',
            'days',
        )
