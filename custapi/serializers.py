from rest_framework import serializers
from api.models import *
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    id =  serializers.IntegerField()