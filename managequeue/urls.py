from .views import *
from django.urls import path

urlpatterns = [
    path('register', Check_Vibe.as_view()),

]