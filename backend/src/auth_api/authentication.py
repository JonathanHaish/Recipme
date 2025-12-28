from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that reads the access token from cookies
    instead of the Authorization header.
    """
    def authenticate(self, request):
        # Try to get token from cookie first
        access_token = request.COOKIES.get('access_token')
        
        if access_token is None:
            # Fallback to Authorization header for flexibility
            return super().authenticate(request)
        
        # Validate the token
        validated_token = self.get_validated_token(access_token)
        
        # Get the user from the validated token
        return self.get_user(validated_token), validated_token

