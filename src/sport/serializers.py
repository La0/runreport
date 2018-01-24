from rest_framework import serializers


class StatsSerializer(serializers.Serializer):
    sports = serializers.SerializerMethodField()
    distances = serializers.SerializerMethodField()
    hours = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'sports',
            'distances',
            'hours',
        )

    def get_sports(self, stats):
        return stats.get_sports()

    def get_distances(self, stats):
        return stats.get_distances()

    def get_hours(self, stats):
        return stats.get_sports()
