from .views import *
from django.urls import path

urlpatterns = [
    path('register', SignupView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('delete',DeleteUser.as_view()),
    path('truncate', TruncateView.as_view()),
    path('settoken', SetTokenView.as_view()),

]