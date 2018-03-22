from rest_framework import serializers
from tracks.models import Track


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = (
            'id',
            'provider',
            'simple',
            'image',
            'thumb',
            # TODO: splits
        )
