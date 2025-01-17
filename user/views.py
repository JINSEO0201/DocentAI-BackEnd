from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.shortcuts import render, redirect
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from supabase import create_client, Client
from django.conf import settings
import requests

# Supabase 클라이언트 설정
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# 1. 프론트엔드에서 로그인 요청
# 2. kakao_login API가 카카오 로그인 창 반환 (auth_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def kakao_login(request):
    redirect_uri = f"{settings.FRONTEND_URL}/auth" # 프론트엔드 url
    
    auth_url = f"{settings.SUPABASE_URL}/auth/v1/authorize?provider=kakao&redirect_to={redirect_uri}"
    return redirect(auth_url)

# 로그인 이후 작동할 로직. 유저 정보를 저장, 토큰 발급 등등
@api_view(['GET'])
@permission_classes([AllowAny])
def kakao_callback(request):
    # access token(supabase) 받기
    access_token = request.data.get('access_token')

    if not access_token:
        return Response({'error': '구글 로그인 중 오류가 발생했습니다.'}, status=status.HTTP_400_BAD_REQUEST)


    # supabase에서 유저 정보 받아오기
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
    }
    response = requests.get(f"{settings.SUPABASE_URL}/auth/v1/user", headers=headers)
    
    if response.status_code == 200:
        supabase_user_info = response.json()  # User info
    

    # 장고 유저 get or create
    user = get_or_create_user_from_supabase(supabase_user_info)

    # Django JWT 생성
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # 쿠키에 담기
    response = Response({'message': 'Login successful'})
    response.set_cookie(
            key='access_token',
            value=access_token,
            )
    # httponly=True,  # JavaScript에서 접근 불가
    response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            )  # httponly=True, secure = True, samesite = 'Lax' 보안 설정정

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout(request):
    # supabase refresh_token 무효화 생략 (다음 로그인 시 자동 갱신)

    access_token = request.COOKIES.get('access_token')
    refresh_token = request.COOKIES.get('refresh_token')

    if not access_token or not refresh_token:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    # 쿠키에서 Access Token과 Refresh Token을 삭제
    response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    # 클라이언트에서 refresh token을 전달받음
    refresh_token = request.COOKIES.get('refresh_token')

    if not refresh_token:
        return Response({'error': 'No refresh token provided'}, status=400)

    try:
        # Refresh Token으로 새로운 Access Token 생성
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)

        response = Response({'message': 'Refresh success'}, status=status.HTTP_200_OK)

        response.set_cookie(
            key='access_token',
            value=new_access_token,
        )

        return response
    except (TokenError, InvalidToken):
        return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


# 보안 강화를 위해 refresh token을 세션 저장소나, 암호화 후 데이터베이스에 저장하는 방법 사용 가능. 추후 개발

# 수파베이스 유저 정보로 장고 유저 만들기
def get_or_create_user_from_supabase(supabase_user_info):
    email = supabase_user_info.get("email")
    full_name = supabase_user_info.get("user_metadata", {}).get("full_name", "Anonymous")
    
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"username": email},
    )

    # User 정보 업데이트
    if created:
        user.full_name = full_name
        user.save()


    return user