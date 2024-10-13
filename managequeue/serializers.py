from rest_framework import serializers
from api.models import *


from rest_framework import serializers

class AudioFeaturesSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)
    acousticness = serializers.FloatField()
    danceability = serializers.FloatField()
    duration_ms = serializers.IntegerField()
    energy = serializers.FloatField()
    instrumentalness = serializers.FloatField()
    key = serializers.IntegerField()
    liveness = serializers.FloatField()
    loudness = serializers.FloatField()
    speechiness = serializers.FloatField()
    tempo = serializers.FloatField()
    time_signature = serializers.IntegerField()
    valence = serializers.FloatField()
