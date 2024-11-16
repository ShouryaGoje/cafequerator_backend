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

            if payload['auth'] == "Cust":
                track_id = data['track_id']
                if False : #vibe check here self.Vibe_Check(user, track_id)
                    return Response({"message":"Vibe not match"}, status=status.HTTP_204_NO_CONTENT)
                else :
                    pass
     
            cafe_queue.add(table_no=payload['tableNum'], track_name=data['track_name'],track_id= data['track_id'], track_img_url=data['track_img_url'],track_artist_name=data['track_artist_name'], time=datetime.datetime.now())

            # Serialize the updated queue and save it back to the database
            track_queue.Queue = pickle.dumps(cafe_queue)
            track_queue.save()

            return Response({"message": f"success"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return detailed serializer errors
    
    def Vibe_Check(self, user, track_id):
        
        # Step 1: Retrieve the user's playlist vector from the database
        try:
            user_parameters = Vibe_Check_Parameters.objects.get(user=user)
            playlist_vector = pickle.loads(user_parameters.playlist_vector)  # Convert binary back to NumPy array
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
        
        # Step 4: Create a vector from the track's audio features
        track_vector = np.array([[track_features['acousticness'], track_features['danceability'], track_features['energy'], 
                                track_features['instrumentalness'], track_features['liveness'], 
                                track_features['loudness'], track_features['speechiness'], 
                                track_features['tempo'], track_features['valence']]])

        # Step 5: Compute cosine similarity between the track vector and the playlist vector
        similarity = cosine_similarity(track_vector, playlist_vector.reshape(1,-1))

        # Step 6: Define a threshold for similarity and return True/False
        threshold = float(env('Vibe_Threshold', default='0.5'))  # Adjust the threshold as per your requirement
        if similarity[0][0] >= threshold:
            return True
        else:
            return False


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
        track_queue= Track_Queue.objects.get(user=user)

        # Deserialize the user's existing queue
        try:
            cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
        except Exception as e:
            return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
        track_queue= Track_Queue.objects.get(user=user)

        # Deserialize the user's existing queue
        try:
            cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
        except Exception as e:
            return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"Next_track": cafe_queue.get_top()}, status=status.HTTP_200_OK)
    
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

        # Get or create the user's track queue
        track_queue= Track_Queue.objects.get(user=user)

        # Deserialize the user's existing queue
        try:
            cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
        except Exception as e:
            return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        cafe_queue.poper()
        # Serialize the updated queue and save it back to the database
        track_queue.Queue = pickle.dumps(cafe_queue)
        track_queue.save()
        return Response({"message": f"success"}, status=status.HTTP_200_OK)


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
            track_queue= Track_Queue.objects.get(user=user)

            # Deserialize the user's existing queue
            try:
                cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
            except Exception as e:
                return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Add the new track to the queue
            data = serializer.validated_data  # Now this will work
            cafe_queue.remove(data['table_no'])

            # Serialize the updated queue and save it back to the database
            track_queue.Queue = pickle.dumps(cafe_queue)
            track_queue.save()

            return Response({"message": f"success"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    