from .backends import CookieJWTAuthentication
from django.contrib.auth.models import AnonymousUser

class JWTUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = CookieJWTAuthentication()

    def __call__(self, request):
        try:
            user, validated_token = self.jwt_authenticator.authenticate(request)
            if user:
                request.user = user
                request._cached_user = user  # Django가 사용하는 _cached_user 설정
                request.token = validated_token
            else:
                request.user = AnonymousUser()
                request._cached_user = AnonymousUser()
        except Exception as e:
            request.user = AnonymousUser()
            request._cached_user = AnonymousUser()

        response = self.get_response(request)
        return response
