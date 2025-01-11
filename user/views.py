from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from supabase import create_client, Client
from django.conf import settings

# Supabase 클라이언트 설정
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# 1. 프론트엔드에서 로그인 요청
# 2. kakao_login API가 카카오 로그인 창 반환 (auth_url)
# 3. 로그인 완료 시 supabase_callback API로 redirect
# 4. supabase_callback API에서 사용자 정보 저장, JWT토큰 발급 이후 HTTP 쿠키 만들어서 프론트에 제공

@api_view(['GET'])
def kakao_login(request):
    redirect_uri = f"{settings.BACKEND_URL}/api/v1/user/supabase/callback" # 인증 후에 해당 링크로 돌아옴
    
    auth_url = f"{settings.SUPABASE_URL}/auth/v1/authorize?provider=kakao&redirect_to={redirect_uri}"
    return redirect(auth_url)

# 로그인 이후 작동할 로직. 유저 정보를 저장, 토큰 발급 등등
@api_view(['GET']) # Supabase에서 redirect 시 GET Method 사용용
def kakao_callback(request):
    code = request.GET.get('code')
    if not code:
        return Response({'error': 'Authorization failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Supabase 서버로 Access Token 요청
    token_response = request.post(
        f"{settings.SUPABASE_URL}/auth/v1/token",
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': settings.KAKAO_REST_API_KEY,
            'client_secret': settings.KAKAO_SECRET_CODE,
            'redirect_uri': f"{settings.BACKEND_URL}/api/v1/user/supabase/callback",
        },
    )

    tokens = token_response.json()

    # Access Token, Refresh Token 저장
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    if not access_token or not refresh_token:
      return Response({'error': 'fail to get token'})
    
    # 쿠키에 토큰 저장 후 redirect
    response = redirect(f"{settings.FRONTEND_URL}/") 
    response.set_cookie('access_token', value=str(access_token)) #httponly=True, secure=True
    response.set_cookie('refresh_token', value=str(refresh_token)) #httponly=True, secure=True
    return response


# 보안 강화를 위해 refresh token을 세션 저장소나, 암호화 후 데이터베이스에 저장하는 방법 사용 가능. 추후 개발