from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from supabase import create_client, Client
from django.conf import settings

# Supabase 클라이언트 설정
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

@api_view(['GET'])
def get_exhibition_list(request):
  try:
    # TODO
    # 전시회 목록 반환환
    pass
  except:
    return Response({'error': 'get exhibition list failed!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
@api_view(['GET'])
def get_exhibition_detail(request, exhibition_id):
  try:
    # TODO
    # 작품 리스트, 대화했던 작품 리스트 반환
    pass
  except:
    return Response({'error': 'get exhibition list failed!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)