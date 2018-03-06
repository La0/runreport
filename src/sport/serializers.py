from rest_framework import serializers
from sport.models import Sport, SportDay, SportWeek, SportSession


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ('id', 'depth', 'parent', 'name', 'slug')


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
    sport = SportSerializer()

    class Meta:
        model = SportSession
        fields = (
            'id',
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
            'created',
            'updated',
        )

class SportDaySerializer(serializers.ModelSerializer):
    sessions = SportSessionSerializer(many=True)

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
