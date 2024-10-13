from .views import *
from django.urls import path

urlpatterns = [
    path('checkvibe', Check_Vibe.as_view()),
    path('add-track', Add_Track.as_view()),
    path('get-queue', Get_Queue.as_view()),

]