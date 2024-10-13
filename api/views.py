from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
from .models import User
import jwt, datetime
from datetime import datetime, timedelta, timezone




class SignupView(APIView):
    def post(self, request):
        serializer = CombinedUserCafeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Registeration Successfully"}, status=status.HTTP_200_OK)
    
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({"error":"User Not Found"},status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({"error":"Incorrect Password"},status=status.HTTP_400_BAD_REQUEST)
        payload = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')


        response = Response()

        # response.set_cookie(key='jwt',
        #                      value=token, 
        #                      httponly=True,
        #                      samesite='None', 
        #                      secure=True)
        response.data = {
            'message': "token set",
            'jwt': f"{token}"}

        response.status_code = 200
        return response
    
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

        # Find the user from the payload
        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            return Response({"error":"User Not Found"},status=status.HTTP_400_BAD_REQUEST)
        

        cafe_info = Cafe_Info.objects.filter(user=user).first()
        token_info = Spotify_Api_Parameters.objects.filter(user=user).first()
        response = Response()
        

        try:
            token_info = SpotifyParameterSerializer(token_info).data
        except:
            token_info = "Not Set"

        response.data = {
            "cafe_info": f"{CafeInfoSerializer(cafe_info).data}",
            "token_info": f"{token_info}"
        }

        response.status_code = 200
        return response

   

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        response.status_code = 200
        return response
    
class DeleteUser(APIView):
   
    def delete(self, request, format=None):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

        # Extract the token
        token = auth_header.split(' ')[1]
        password = request.data['password']

        if not token:
            return Response({"error": "Unauthenticated User"}, status=status.HTTP_401)

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=payload['id']).first()

        if not user.check_password(password):
            return Response({"error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({"message": "User Deleted Successfully"}, status=status.HTTP_200_OK)


class TruncateView(APIView):
    def post(self, request, format = None):
        User.objects.all().delete()

        return Response({"message":"Data Gone"},status=status.HTTP_410_GONE)
    

class SetTokenView(APIView):
    def post(self, request, format=None):
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

        # Validate the incoming request data using the serializer
        serializer = SpotifyParameterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            access_token = serializer.validated_data.get("access_token")
            refresh_token = serializer.validated_data.get("refresh_token")
            expires_at = serializer.validated_data.get("expires_at")

            # Check if the Spotify parameters already exist for the user
            spotify_params, created = Spotify_Api_Parameters.objects.update_or_create(
                user=user,
                defaults={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_at": expires_at  # Save the Unix timestamp as an integer
                }
            )

            return Response({"message": "Spotify token set"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
