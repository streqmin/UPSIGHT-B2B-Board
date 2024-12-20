from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None  # 토큰 없음

        try:
            validated_token = self.get_validated_token(access_token)
        except InvalidToken as e:
            # InvalidToken의 상세 메시지 분석
            error_detail = getattr(e, "detail", None)
            if error_detail and isinstance(error_detail, dict):
                messages = error_detail.get("messages", [])
                for msg in messages:
                    # 만료된 토큰인지 확인
                    if "만료된" in str(msg.get("message", "")) or "expired" in str(msg.get("message", "")):
                        raise AuthenticationFailed("Access token has expired.")  # 만료 메시지 반환
            raise AuthenticationFailed("Invalid token.")  # 기본 메시지
        except TokenError:
            raise AuthenticationFailed("Token error.")  # 기타 토큰 에러

        user = self.get_user(validated_token)
        if user is None or not user.is_active:
            raise AuthenticationFailed("User is inactive.")

        return (user, validated_token)