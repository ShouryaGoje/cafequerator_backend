from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class CafeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cafe_Info
        fields = ['Cafe_Name', 'Cafe_Address', 'Cafe_Contact', 'Owner_Name', 'Owner_Contact', 'No_of_Tables']


class CombinedUserCafeSerializer(serializers.ModelSerializer):
    cafe_info = CafeInfoSerializer()  # Nesting the CafeInfoSerializer inside the User serializer

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'cafe_info']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Extract cafe_info data
        cafe_info_data = validated_data.pop('cafe_info', None)
        
        # Create User instance
        password = validated_data.pop('password', None)
        user_instance = self.Meta.model(**validated_data)
        
        if password is not None:
            user_instance.set_password(password)
        user_instance.save()
        
        # Create Cafe_Info instance
        if cafe_info_data:
            Cafe_Info.objects.create(user=user_instance, **cafe_info_data)
        for i in range(1, int(cafe_info_data['No_of_Tables'])+1):
            Table_Status_Data.objects.create(user=user_instance, table_number=i)
        
        return user_instance
    
class SpotifyParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spotify_Api_Parameters
        fields = ["access_token","refresh_token","expires_at"]


class PlaylistVectorSerializer(serializers.Serializer):

    playlist_name = serializers.CharField()
    playlist_id = serializers.CharField()

class TableStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table_Status_Data
        fields = ["table_number","table_status"]


            
