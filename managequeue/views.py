from api.models import *
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
import jwt, datetime
from managequeue.CafeQueue import CafeQueue as cq
import pickle

# Create your views here.
 

class Check_Vibe(APIView):
    
    def post(self, request):
        serializer = AudioFeaturesSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            #dummy if else
            if True:
                return Response({'message': 'vibe match'}, status = status.HTTP_202_ACCEPTED)
            
            else:
                pass

        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
    
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
            cafe_queue.add(data['table_no'], data['track_name'], data['track_id'], datetime.datetime.now())

            # Serialize the updated queue and save it back to the database
            track_queue.Queue = pickle.dumps(cafe_queue)
            track_queue.save()

            return Response({"message": f"success"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return detailed serializer errors
    
    

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
        
        return Response({"Queue": f"{cafe_queue.getqueue()}"}, status=status.HTTP_200_OK)

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
        
        return Response({"Queue": f"{cafe_queue.get_top()}"}, status=status.HTTP_200_OK)
    
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
        return Response({"message": f"success"}, status=status.HTTP_200_OK)


class Remove_table(APIView):
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

            return Response({"message": f"success"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    