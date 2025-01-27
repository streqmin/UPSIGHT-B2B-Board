from django.views.generic import TemplateView
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from rest_framework import generics, viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import RegisterSerializer, BusinessSerializer
from .models import Business, BusinessMember
from authentication.permissions import IsBusinessAdmin


class RegisterTemplateView(TemplateView):
    template_name = 'authentication/register.html'
class LoginTemplateView(TemplateView):
    template_name = 'authentication/login.html'

    def get(self, request, *args, **kwargs):
        # 이미 인증된 사용자라면 로그인 페이지 대신 메인 페이지로 이동
        if request.user.is_authenticated:
            return redirect('boards:board_main')
        # 미인증 사용자라면 로그인 템플릿 렌더링
        return super().get(request, *args, **kwargs)

# JWT를 쿠키에 넣는 커스텀 로그인 뷰
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is None:
            raise AuthenticationFailed('Invalid username or password.')

        # 기본 JWT 발급 로직 실행
        response = super().post(request, *args, **kwargs)
        data = response.data

        # 발급된 JWT를 응답 본문에서 제거하고, 쿠키로 내려주기
        access_token = data.pop('access', None)
        refresh_token = data.pop('refresh', None)

        # 로그인 성공 메시지만 응답 본문에 담음
        response = Response({'message': 'Login successful'}, status=response.status_code)
        if access_token:
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,   # JavaScript에서 접근 불가 (보안 강화)
                secure=True,     # HTTPS에서만 전송 (개발 환경에서는 False 가능)
                samesite='Lax'   # CSRF 방지
            )
        if refresh_token:
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=True,
                samesite='Lax'
            )
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "No refresh token provided in cookie."}, status=400)

        # refresh_token을 data에 직접 넣어서 Serializer 호출
        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            # 토큰이 만료되었거나 잘못된 경우
            raise AuthenticationFailed(e.args[0])

        # 유효한 경우 새 access token 반환
        response_data = serializer.validated_data
        access_token = response_data.get('access')

        if not access_token:
            return Response({"detail": "Access token could not be refreshed."}, status=400)

        response = Response(response_data, status=200)
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        return response

class LogoutView(TokenBlacklistView):
    """
    SimpleJWT의 TokenBlacklistView를 상속하여 로그아웃 기능 구현.
    """
    
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        access_token = request.COOKIES.get('access_token')

        if not refresh_token and not access_token:
            return Response({"detail": "No refresh_token or access_token found in cookies."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass
        except Exception:
            pass

        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')
        return response

# 사용자 등록을 위한 뷰
class RegisterView(generics.CreateAPIView):
    """
    새로운 BusinessMember (사용자)을 등록하는 API 엔드포인트.
    모든 사용자가 접근할 수 있습니다.
    """
    queryset = BusinessMember.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

# 비즈니스 관리용 뷰셋
class BusinessViewSet(viewsets.ModelViewSet):
    """
    Business 모델의 CRUD (생성, 조회, 수정, 삭제) 기능을 제공하는 뷰셋.
    오직 비즈니스 관리자(Admin)만 접근할 수 있습니다.
    """
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name', 'address', 'phone_number', 'website']
    ordering_fields = ['name']
    ordering = ['name']
    
    def perform_authentication(self, request):
        """list 요청에서는 강제 인증을 수행하지 않음"""
        if getattr(self, "action", None) == "list":
            request.user = None  # 인증을 요구하지 않도록 설정
        else:
            super().perform_authentication(request)
    
    def get_permissions(self):
        """list 요청에서는 AllowAny, 나머지 요청은 IsBusinessAdmin 적용"""
        if getattr(self, "action", None) == "list":
            return [permissions.AllowAny()]
        return [IsBusinessAdmin()]
