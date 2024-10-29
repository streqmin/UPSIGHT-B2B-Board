from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # 쿠키에서 access_token을 가져옴
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None  # 토큰이 없으면 None을 반환하여 인증을 수행하지 않음
        
        # 부모 클래스의 메소드를 사용하여 검증
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
