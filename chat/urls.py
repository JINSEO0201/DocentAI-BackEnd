from django.urls import path
from .views import Chat

urlpatterns = [
    path('chat/<int:exhibition_id>/<int:artwork_id>', Chat.as_view() , name='chat'),
]