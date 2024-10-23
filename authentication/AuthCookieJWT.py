from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def get_raw_token(self, request):
        # 기본적으로 Authorization 헤더에서 토큰을 찾지만, 여기서는 쿠키에서 토큰을 찾음
        return request.COOKIES.get('access_token')
