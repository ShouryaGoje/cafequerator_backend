from api.models import *
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
import jwt, datetime

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






