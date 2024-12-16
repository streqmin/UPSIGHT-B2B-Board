from .backends import CookieJWTAuthentication
from django.contrib.auth.models import AnonymousUser

class JWTUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = CookieJWTAuthentication()

    def __call__(self, request):
        # JWT 토큰을 이용해 사용자 인증
        try:
            user, validated_token = self.jwt_authenticator.authenticate(request)
            request.user = user
            request.token = validated_token
        except Exception:
            # 인증 실패 시 익명 사용자로 설정
            request.user = AnonymousUser()

        response = self.get_response(request)
        return response
