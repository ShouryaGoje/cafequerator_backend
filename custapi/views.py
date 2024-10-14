from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
from .models import *
import jwt, datetime
from datetime import datetime, timedelta, timezone


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data = request.data)

        if serializer.is_valid():
            id = serializer.validated_data['id']
            user = User.objects.filter(id=id).first()
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
                'jwt': f"{token}"}

            response.status_code = 200
            return response


