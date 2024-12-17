from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None

        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
        except InvalidToken as e:
            raise AuthenticationFailed("Invalid token.")
        except TokenError as e:
            raise AuthenticationFailed("Token error: " + str(e))
        except Exception as e:
            raise AuthenticationFailed(str(e))

        if user is None or not user.is_active:
            raise AuthenticationFailed("User is inactive.")

        return (user, validated_token)