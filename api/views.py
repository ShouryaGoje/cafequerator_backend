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

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': "token set"}

        response.status_code = 200
        return response
    
    def get(self,request):
     
        token = request.COOKIES.get('jwt')
        # Check if the token exists
        if not token:
            return Response({"error": "Unauthenticated User"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the JWT token to get the payload
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user from the payload
        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            return Response({"error":"User Not Found"},status=status.HTTP_400_BAD_REQUEST)
        

        cafe_info = Cafe_Info.objects.filter(user=user).first()
        token_info = Spotify_Api_Parameters.objects.filter(user=user).first()
        response = Response()
        

        try:
            token_info = { SpotifyParameterSerializer(token_info).data}
        except:
            token_info = "Not Set"

        response.set_cookie(key='jwt', value=token, httponly=True)
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
   
    def delete(self, request, foramt = None):
        token = request.COOKIES.get('jwt')
        password = request.data['password']

        if not token:
            return Response({"error":"Unauthenticated User"},status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError as e:
            return Response({"error":f"{e}"},status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=payload['id']).first()

        if not user.check_password(password):
            return Response({"error":"Incorrect Password"},status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        return Response({"message":"User Deleted Successfully"}, status=status.HTTP_200_OK)


class TruncateView(APIView):
    def post(self, request, format = None):
        User.objects.all().delete()

        return Response({"message":"Data Gone"},status=status.HTTP_410_GONE)
    

class SetTokenView(APIView):
    def post(self, request, format=None):
        token = request.COOKIES.get('jwt')

        # Check if the token exists
        if not token:
            return Response({"error": "Unauthenticated User"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the JWT token to get the payload
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user from the payload
        user = User.objects.filter(id=payload['id']).first()

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

            # Return the serialized data of the spotify_params
            return Response({"message": "token set"}, status=status.HTTP_200_OK)
        
        return Response({"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)