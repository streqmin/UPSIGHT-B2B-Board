from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # 쿠키에서 access_token 가져오기
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None  # 인증 정보가 없으면 None 반환

        # 토큰을 검증하고 사용자 인증
        validated_token = self.get_validated_token(access_token)
        user = self.get_user(validated_token)

        if user is None or not user.is_active:
            raise AuthenticationFailed("유효하지 않은 사용자입니다.")

        return (user, validated_token)
