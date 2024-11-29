from api.models import *
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
import jwt, datetime
from managequeue.CafeQueue import CafeQueue as cq
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from spotipy import Spotify
from pathlib import Path
import os
import environ
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer





# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Create your views here.
 
    
class Add_Track(APIView):
    def post(self, request):
        # Validate the incoming data using the serializer
        serializer = AddTrackSerializer(data=request.data)
        if serializer.is_valid():  # Corrected to call the method
            # Check for the Authorization header and extract the JWT token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

            token = auth_header.split(' ')[1]

            try:
                # Decode the JWT token to get the user information
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            except jwt.ExpiredSignatureError as e:
                return Response({"error": f"Token expired: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.InvalidTokenError as e:
                return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the user from the decoded payload
            user = User.objects.filter(id=payload['id']).first()
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get or create the user's track queue
            track_queue, created = Track_Queue.objects.get_or_create(user=user)

            # Deserialize the user's existing queue
            try:
                cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
            except Exception as e:
                return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Add the new track to the queue
            data = serializer.validated_data  # Now this will work
            if payload['auth'] == "Admin":
                for i in cafe_queue.getqueue():
                    if i['track_id'] == data['track_id']:
                        if i['id'] == -1:
                            cafe_queue.remove_track(-1,data['track_id'])
                        else:
                            return Response({"message":"Track already in queue"}, status=status.HTTP_226_IM_USED)
                
            if payload['auth'] == "Cust":
                if Table_Status_Data.objects.filter(user = user,table_number= payload['tableNum']).first().table_status == False:
                    return Response({"error":"unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
                track_id = data['track_id']
                if self.Vibe_Check(user, track_id):
                    return Response({"message":"Vibe not match"}, status=status.HTTP_403_FORBIDDEN)
                else :
                    for i in cafe_queue.getqueue():
                        if i['track_id'] == data['track_id']:
                            if i['id'] == -1:
                                cafe_queue.remove_track(-1,data['track_id'])
                            else:
                                return Response({"message":"Track already in queue"}, status=status.HTTP_226_IM_USED)

            
     
            cafe_queue.add(table_no=payload['tableNum'], track_name=data['track_name'],track_id= data['track_id'], track_img_url=data['track_img_url'],track_artist_name=data['track_artist_name'], time=datetime.datetime.now())

            # Serialize the updated queue and save it back to the database
            track_queue.Queue = pickle.dumps(cafe_queue)
            track_queue.save()
            room_name = f"queue_{payload['id']}"
            print(room_name)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
            room_name,
            {
                "type": "websocket.message",  # Must match the method name in the consumer
                "text": "queue updated"
            }
            )
            return Response({"message": f"success"}, status=status.HTTP_200_OK)
        
        
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return detailed serializer errors
    
    def Vibe_Check(self, user, track_id):
        # Define the percentage thresholds for each feature
        matching_tracks = 0
        thresholds = {
            'acousticness': 0.40,
            'danceability': 0.40,
            'energy': 0.40,
            'key': 0.10,
            'instrumentalness': 0.40,
            'loudness': 0.200,
            'mode': 0.00,  # Special case for mode (exact match)
            'tempo': 0.20,
            'time_signature': 0.25,
            'valence': 0.20
        }
        # Step 1: Retrieve the user's playlist vector from the database
        try:
            user_parameters = Vibe_Check_Parameters.objects.get(user=user)
            playlist_df = pickle.loads(user_parameters.playlist_vector)  # Convert binary back to NumPy array
        except Vibe_Check_Parameters.DoesNotExist:
            return False  # No playlist vector found for the user

        # Step 2: Initialize Spotify client to get the track's audio features
        token_info = Spotify_Api_Parameters.objects.filter(user=user).first()
        access_token = token_info.access_token

        if not access_token:
            return False  # No access token available

        sp = Spotify(auth=access_token)

        # Step 3: Retrieve the track's audio features
        audio_features = sp.audio_features(track_id)
        
        if not audio_features or audio_features[0] is None:
            return False  # Track not found or no audio features available

        track_features = audio_features[0]
        
        print(track_features)

        ##############################################################################################################

        for playlist_feature in playlist_df.to_dict('records'):
            
            similarity_percentage = self.compare_tracks(playlist_feature, track_features, thresholds)
        
            # Check if similarity is greater than or equal to 50%
            if similarity_percentage >= 50:
                
                matching_tracks += 1

        total_tracks = len(playlist_df)
        
        threshold = total_tracks * 0.5  # 50% of total tracks
        ##############################################################################################################

        if matching_tracks >= threshold:
            return False
        else:
            return True
    
    def compare_tracks(self,track_features, comparison_features, thresholds):
        
        similarity_count = 0
        features = thresholds.keys()
        
        for feature in features:
            track_value = track_features[feature]
            comparison_value = comparison_features[feature]
            threshold_percentage = thresholds[feature]
            
            if self.compare_features(track_value, comparison_value, threshold_percentage):
                similarity_count += 1
    
        # Calculate similarity as a percentage of matching features
        similarity_percentage = (similarity_count / len(features)) * 100
        return similarity_percentage
    def compare_features(self,track_value, comparison_value, threshold_percentage):
            lower_bound = track_value - (track_value * threshold_percentage)
            upper_bound = track_value + (track_value * threshold_percentage)
            return lower_bound <= comparison_value <= upper_bound

class Get_Queue(APIView):

    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        try:
            # Decode the JWT token to get the user information
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError as e:
            return Response({"error": f"Token expired: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError as e:
            return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user from the decoded payload
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's track queue
        print(payload['id'])
        # Deserialize the user's existing queue
        try:
            track_queue= Track_Queue.objects.get(user=user)
            cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
        except Exception as e:
            return Response({"error": f"Queue empty: {e}"}, status=status.HTTP_400_BAD_REQUEST)#changed status from 500 to 400
        
        return Response({"Queue": cafe_queue.getqueue()}, status=status.HTTP_200_OK)

class Next_Track(APIView):

    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        try:
            # Decode the JWT token to get the user information
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError as e:
            return Response({"error": f"Token expired: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError as e:
            return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        if payload['auth']!= 'Admin':
            return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Fetch the user from the decoded payload
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's track queue
        

        # Deserialize the user's existing queue
        try:
            track_queue= Track_Queue.objects.get(user=user)
            cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
        except Exception as e:
            return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
        next_track=cafe_queue.get_top()
        if next_track is None:
            return Response({"error": f"Kuch nai hai queue me"}, status=status.HTTP_204_NO_CONTENT)
        Track_Queue.objects.filter(user=user).update(current_track = next_track)
        return Response({"Next_track": next_track}, status=status.HTTP_200_OK)
    
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]


        try:
            # Decode the JWT token to get the user information
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError as e:
            return Response({"error": f"Token expired: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError as e:
            return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        if payload['auth']!= 'Admin':
            return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Fetch the user from the decoded payload
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            track_queue= Track_Queue.objects.get(user=user)
            cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
        except Exception as e:
            return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        cafe_queue.poper()
        # Serialize the updated queue and save it back to the database
        track_queue.Queue = pickle.dumps(cafe_queue)
        track_queue.save()
        room_name = f"queue_{payload['id']}"
        print(room_name)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        room_name,
        {
            "type": "websocket.message",  # Must match the method name in the consumer
            "text": "queue updated"
        }
        )
        async_to_sync(channel_layer.group_send)(
        room_name,
        {
            "type": "websocket.message",  # Must match the method name in the consumer
            "text": "current track updated"
        }
        )
        return Response({"message": f"success"}, status=status.HTTP_200_OK)


class Current_Track(APIView):

    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        try:
            # Decode the JWT token to get the user information
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError as e:
            return Response({"error": f"Token expired: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError as e:
            return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)


        # Fetch the user from the decoded payload
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's track queue
        

        # Deserialize the user's existing queue
        try:
            track_queue= Track_Queue.objects.get(user=user)
        except Exception as e:
            return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_404_NOT_FOUND)
    
        return Response({"current_track": track_queue.current_track}, status=status.HTTP_200_OK)


class Remove_Table(APIView):
    def post(self, request):
        # Validate the incoming data using the serializer
        serializer = RemoveTableSerializer(data=request.data)
        if serializer.is_valid():  # Corrected to call the method
            # Check for the Authorization header and extract the JWT token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

            token = auth_header.split(' ')[1]

            try:
                # Decode the JWT token to get the user information
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            except jwt.ExpiredSignatureError as e:
                return Response({"error": f"Token expired: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.InvalidTokenError as e:
                return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            if payload['auth']!= 'Admin':
                return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

            # Fetch the user from the decoded payload
            user = User.objects.filter(id=payload['id']).first()
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get or create the user's track queue
            
            # Deserialize the user's existing queue
            try:
                track_queue= Track_Queue.objects.get(user=user)

                cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
            except Exception as e:
                return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Add the new track to the queue
            data = serializer.validated_data  # Now this will work
            cafe_queue.remove(data['table_no'])

            # Serialize the updated queue and save it back to the database
            track_queue.Queue = pickle.dumps(cafe_queue)
            track_queue.save()
            Table_Status_Data.objects.filter(user=user, table_number =data['table_no']).update(table_status = False)
            room_name = f"queue_{payload['id']}"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
            room_name,
            {
                "type": "websocket.message",  # Must match the method name in the consumer
                "text": "queue updated"
            }
            )
            return Response({"message": f"success"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    