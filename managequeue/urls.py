from .views import *
from django.urls import path

urlpatterns = [
    path('checkvibe', Check_Vibe.as_view()),

]