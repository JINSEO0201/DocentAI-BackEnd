from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from supabase import create_client, Client
from django.conf import settings
from .models import Chat

# Supabase 클라이언트 설정
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

class Chat(APIView):
  def get(self, request, exhibition_id, artwork_id): # 채팅방 입장 API
    user = request.user
    user_access = user.access

    # 유저 정보 받아오기
    user_supabase = supabase.auth.get_user(user_access)
    user_id_supabase = user_supabase.user.id
    
    chat_history = supabase.table('chat').select('chat_history').eq('artwork_id', artwork_id).eq('user_id', user_id_supabase).execute()

    return Response(chat_history.data, status=status.HTTP_200_OK)

  def post(self, request, exhibition_id, artwork_id): # 채팅하기 API
    user = request.user
    question = request.data.get('question')
    chat_id = request.data.get('chat_id')

    message = ''
    questions = []
    # TODO LLM 통신하기
    # message, questions 변수에 LLM response 정리


    # db.sqlite3에 임시 저장
    chat = Chat.objects.create(user=user, artwork_id=artwork_id, exhibition_id=exhibition_id, chat_history=[])

    if questions and message:
      return Response({'message': message, 'questions': questions}, status=status.HTTP_200_OK)

    else:
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
  def delete(self, request, exhibition_id, artwork_id):
    # db.sqlite3 비우기
    # supabase에 post
    return 0
