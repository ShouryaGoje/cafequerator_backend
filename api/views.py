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
        return Response(serializer.data)
    
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

        cafe_info = Cafe_Info.objects.filter(user=user).first()
        response = Response()


        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': "token set",
            "data": f"{CafeInfoSerializer(cafe_info).data}"

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
   
    def post(self, request, foramt = None):
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