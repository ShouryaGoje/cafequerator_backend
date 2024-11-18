from .views import *
from django.urls import path
from . import consumers

urlpatterns = [
    path('add-track', Add_Track.as_view()),
    path('get-queue', Get_Queue.as_view()),
    path('next-track', Next_Track.as_view()),
    path('remove-table', Remove_Table.as_view()),
    path('current-track', Current_Track.as_view()),
    path("ws/queue", consumers.QueueConsumer.as_asgi())
]