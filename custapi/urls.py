from .views import *
from django.urls import path

urlpatterns = [
    path('login', LoginView.as_view()),
    path('access-token', GetAccessToken.as_view()),
]