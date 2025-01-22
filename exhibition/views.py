from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from supabase import create_client, Client
from django.conf import settings

# Supabase 클라이언트 설정
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_exhibition_list(request):
  try:
    exhibitions = supabase.table('exhibition').select('*').execute()

    # 데이터 정리
    exhibition_list = []
    for exhibition in exhibitions:
        exhibition_data = {
          'exhibitionId': exhibition['id'],
          'exhibitionName': exhibition['name'],
          'exhibitionImageUrl': exhibition['image_url'],
          'exhibitionDescription': exhibition['description'],
          'exhibitionPeriod': exhibition['period']
        }
        exhibition_list.append(exhibition_data)
    
    return Response(exhibition_list, status=status.HTTP_200_OK)
  except:
    return Response({'error': 'get exhibition list failed!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
@api_view(['GET'])
@permission_classes([AllowAny])
def get_exhibition_detail(request, exhibition_id):
  result = {}

  # 작품 리스트 (artworks)
  artworks = supabase.table('artwork').select('*').eq('exhibition_id', exhibition_id).execute()

  artwork_list = []
  for artwork in artworks:
    artwork_data = {
      'artworkId': artwork.id,
      'artworkTitle': artwork.title,
      'artistName': artwork.artist,
      'artworkImageUrl': artwork.image_url,
      'artworkDescription': artwork.description
    }
    artwork_list.append(artwork_data)

  # 대화했던 작품 리스트 (chats)
  try:
    user = request.user
    user_access = user.access

    # 유저 정보 받아오기
    user_supabase = supabase.auth.get_user(user_access)
    user_id_supabase = user_supabase.user.id

    chats = supabase.table('chat').select('id').eq('exhibition_id', exhibition_id).eq('user_id', user_id_supabase).execute()

    chat_list = []
    for artwork in artworks:
      if artwork.chat_id in chats.data:
        chat_list_data = {
          'chatId': artwork.chat_id,
          'artworkId': artwork.id,
          'artworkTitle': artwork.title,
          'artistName': artwork.artist
        }
        chat_list.append(chat_list_data)

  except:
    chat_list = []
  
  result['artworks'] = artwork_list
  result['chats'] = chat_list

  return Response(result, status=status.HTTP_200_OK)