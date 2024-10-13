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
        serializers = AddTrackSerializer(data = request.data)
        if serializers.is_valid:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

            # Extract the token
            token = auth_header.split(' ')[1]

            # Check if the token exists
            if not token:
                return Response({"error": "JWT token missing from cookies"}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                # Decode the JWT token to get the payload
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            except jwt.ExpiredSignatureError as e:
                return Response({"error": f"Token expired: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.InvalidTokenError as e:
                return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)

            # Find the user from the payload
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
            data = serializers.validated_data
            cafe_queue.add(data['table_no'], data['track_name'], data['track_id'], datetime.datetime.now())

            # Serialize the updated queue and save it back to the database
            track_queue.Queue = pickle.dumps(cafe_queue)
            track_queue.save()

            return Response({"Queue": f"{cafe_queue.getqueue()}"}, status=status.HTTP_200_OK)
        return Response({"error": f"Bad request"} ,status=status.HTTP_400_BAD_REQUEST)









