from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import pickle
from managequeue.CafeQueue import CafeQueue as cq
from jsonfield import JSONField

empty_queue = pickle.dumps(cq())

# Create your models here.
class User(AbstractUser):
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Cafe_Info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Cafe_Name = models.CharField(max_length=255,default='')
    Cafe_Address = models.CharField(max_length=500,default='')
    Cafe_Contact = models.CharField(max_length=15,default='')
    Owner_Name = models.CharField(max_length=255,default='')
    Owner_Contact = models.CharField(max_length=15,default='')
    No_of_Tables = models.IntegerField(default=1)

class Table_Status_Data(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table_number = models.IntegerField()
    table_status = models.BooleanField(default=False)
    
class Spotify_Api_Parameters(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500)
    expires_at = models.CharField(max_length=500)

class Vibe_Check_Parameters(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    playlist_vector  = models.BinaryField(default=empty_queue)

class Track_Queue(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Queue = models.BinaryField(default=empty_queue)
    current_track = JSONField(default={})

