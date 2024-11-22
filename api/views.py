from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
from .models import *
import jwt
from datetime import datetime, timedelta, timezone
import io
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from .models import Cafe_Info
from PIL import Image
import tempfile
import os
import spotipy
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from managequeue.CafeQueue import CafeQueue as cq
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



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
            'auth': 'Admin',
            'tableNum':0,
            'exp': datetime.now(timezone.utc) + timedelta(weeks=4),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')


        response = Response()

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
        
        if payload['auth']!= 'Admin':
            return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Find the user from the payload
        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            return Response({"error":"User Not Found"},status=status.HTTP_400_BAD_REQUEST)
        

        cafe_info = Cafe_Info.objects.filter(user=user).first()
        token_info = Spotify_Api_Parameters.objects.filter(user=user).first()
        response = Response()
        

       
        token_info = SpotifyParameterSerializer(token_info).data
        if token_info["access_token"] == '':
            token_info = "Not set"
        
        table_status = Table_Status_Data.objects.filter(user=user)
        table_status = TableStatusSerializer(table_status, many = True).data
        response.data = {
            "cafe_info": CafeInfoSerializer(cafe_info).data,
            "id" : payload['id'],
            "token_info": token_info,
            "table_status": table_status
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
        if payload['auth']!= 'Admin':
            return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(id=payload['id']).first()

        if not user.check_password(password):
            return Response({"error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({"message": "User Deleted Successfully"}, status=status.HTTP_200_OK)


class TruncateView(APIView):
    def post(self, request, format = None):
        User.objects.all().delete()

        return Response({"message":"Data Gone"},status=status.HTTP_410_GONE)
    
class TableStatusView(APIView):
    def get(self, request, format = None):
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
        
        if payload['auth']!= 'Admin':
            return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Find the user from the payload
        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            return Response({"error":"User Not Found"},status=status.HTTP_400_BAD_REQUEST)
        table_status = Table_Status_Data.objects.filter(user=user)
        table_status = TableStatusSerializer(table_status, many = True).data
        
        return Response({"table_status": table_status}, status=status.HTTP_200_OK)

        
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
        if payload['auth']!= 'Admin':
            return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

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
    



class PdfAPIView(APIView):
    def post(self, request, format=None):
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

        # Extract the token
        token = auth_header.split(' ')[1]

        # Check if the token exists
        if not token:
            return Response({"error": "JWT token missing"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Decode the JWT token to get the payload
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError as e:
            return Response({"error": f"Token expired: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError as e:
            return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        if payload['auth']!= 'Admin':
            return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Find the user from the payload
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch cafe info using user
        try:
            cafe_info = Cafe_Info.objects.get(user=user)
            cafe_name = cafe_info.Cafe_Name
            no_of_tables = cafe_info.No_of_Tables  # Fetching No_of_Tables from Cafe_Info
        except Cafe_Info.DoesNotExist:
            return Response({"error": "Cafe not found"}, status=status.HTTP_404_NOT_FOUND)

        # Set up PDF response
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        base_url = "https://cafe-querator.vercel.app"  # Hardcoded URL

        # Generate QR codes for each table
        for table_num in range(1, no_of_tables + 1):
            # Create the URL
            qr_url = f"{base_url}/{cafe_name}/table/{table_num}?id={user.id}"

            # Generate QR code using Pillow (PIL)
            qr = qrcode.make(qr_url)  # This returns a PIL Image object

            # Save the QR code to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                qr.save(tmp_file, format='PNG')  # Save it as a PNG image
                tmp_file_path = tmp_file.name  # Get the temporary file path
            
            # Place the QR code on the PDF page
            qr_x_position = (width - 300) / 2  # Horizontal center
            qr_y_position = (height - 300) / 2 + 100  # Positioned slightly higher to leave space for text below

            # Place the QR code on the PDF page
            pdf.drawImage(tmp_file_path, qr_x_position, qr_y_position, 300, 300)

            # Add the "Table No. X" text below the QR code
            text_x_position = (width - 300) / 2 + 100  # Center text below the QR code
            text_y_position = qr_y_position - 40  # Position text 40 units below the QR code
            pdf.setFont("Helvetica", 14)  # Set font and size for the table number text
            pdf.drawString(text_x_position, text_y_position, f"Table No. {table_num}")

            # Add a new page for the next table
            pdf.showPage()

            # Optionally, delete the temporary file after it's used
            os.remove(tmp_file_path)

        # Save the PDF
        pdf.save()
        buffer.seek(0)

        # Create a response with the PDF content
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{cafe_name}_table_qrcodes.pdf"'

        return response
    


class SetPlaylistVector(APIView):
    def post(self, request):
        serializer = PlaylistVectorSerializer(data=request.data)
        if serializer.is_valid():
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({"error": "Authorization header missing or improperly formatted"}, status=status.HTTP_401_UNAUTHORIZED)

            # Extract the token
            token = auth_header.split(' ')[1]

            # Check if the token exists
            if not token:
                return Response({"error": "JWT token missing"}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                # Decode the JWT token to get the payload
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            except jwt.ExpiredSignatureError as e:
                return Response({"error": f"Token expired: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.InvalidTokenError as e:
                return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has the correct authorization
            if payload['auth'] != 'Admin':
                return Response({"error": "API Access not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
            print(payload['id'])
            # Find the user from the payload
            user = User.objects.filter(id=payload['id']).first()
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Get the user's Spotify access token from the database
            token_info = Spotify_Api_Parameters.objects.filter(user=user).first()
            token_info = SpotifyParameterSerializer(token_info).data
            if token_info["access_token"] == '':
                return Response({"error": "Access token not found"}, status=status.HTTP_404_NOT_FOUND)

            access_token = token_info["access_token"]
            playlist_id = serializer.validated_data['playlist_id']

            # Initialize Spotify client with access token
            sp = spotipy.Spotify(auth=access_token)

            # Fetch playlist tracks and their audio features
            try:
                tracks = self.get_playlist_tracks(sp, playlist_id)
            except spotipy.SpotifyException as e:
                return Response({"error": f"Spotify API Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
           
            tracks_info = [ (track['track']['id'],track['track']['name'])for track in tracks]
            #############################################################################: add Playlist code here 
            audio_features = self.extract_audio_features(sp,[track_ids[0] for track_ids in tracks_info])
            if audio_features is None:
                return Response({"error":"error with playlist features"}, status=status.HTTP_205_RESET_CONTENT)
            df = pd.DataFrame(audio_features)
            
            Vibe_Check_Parameters.objects.update_or_create(
                user=user, 
                defaults={'playlist_vector': pickle.dumps(df)}  # Serialize the vector
            )
        
            
            #############################################################################: do not change after this

            # Get or create the user's track queue
            track_queue, created = Track_Queue.objects.get_or_create(user=user)

            # Deserialize the user's existing queue
            try:
                cafe_queue = pickle.loads(track_queue.Queue) if track_queue.Queue else cq()
            except Exception as e:
                return Response({"error": f"Failed to load queue: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                cafe_queue.remove(-1)
            except Exception as e:
                pass
            for track_info in tracks_info: 
                cafe_queue.add(table_no=-1, track_name=track_info[1],track_id= track_info[0], track_img_url='-',track_artist_name='-', time=datetime.now())
            track_queue.Queue = pickle.dumps(cafe_queue)
            track_queue.save()
            
            return Response({"message": "Playlist vector updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Define the helper functions with `self`
    def get_playlist_tracks(self, sp, playlist_id):
        tracks = []
        response = sp.playlist_tracks(playlist_id)
        while response:
            tracks.extend(response['items'])
            if response['next']:
                response = sp.next(response)
            else:
                response = None
        return tracks

    def extract_audio_features(self, sp, track_ids):
        try:
            audio_features = sp.audio_features(tracks=track_ids)
        except:
            android_features =None
        return audio_features

    
