from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
from api.serializers import SpotifyParameterSerializer
from api.models import *
import jwt, datetime
from datetime import datetime, timedelta, timezone


class LoginView(APIView):
    def get(self, request):
        serializer = LoginSerializer(data = request.data)

        if serializer.is_valid():
            cafeId = int(serializer.validated_data['cafeId'])
            user = User.objects.filter(id=cafeId).first()
            if user is None:
                return Response({"error":"User Not Found"},status=status.HTTP_400_BAD_REQUEST)
            payload = {
                'id': user.id,
                'auth': 'Cust',
                'exp': datetime.now(timezone.utc) + timedelta(hours=2),
                'iat': datetime.now(timezone.utc)
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')


            response = Response()

            response.data = {
                'message': "token set",
                'cjwt': f"{token}"}

            response.status_code = 200
            return response
        return Response({"message":"nooooooo"}, status=status.HTTP_400_BAD_REQUEST) 


class GetAccessToken(APIView):
    def get(self,request):
     
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
        
        if payload['auth']!= 'Cust':
            return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Find the user from the payload
        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            return Response({"error":"User Not Found"},status=status.HTTP_400_BAD_REQUEST)
        
        token_info = Spotify_Api_Parameters.objects.filter(user=user).first()
        response = Response()
        

       
        access_token = SpotifyParameterSerializer(token_info).data["access_token"]
        if access_token == '':
            access_token = "Not set"
        

        response.data = {
            "access_token": access_token
        }

        response.status_code = 200
        return response
    
