from rest_framework import permissions
from django.conf import settings

class IsInternalApp(permissions.BasePermission):
    """
    Allows access only if the internal API Key is sent in the request Header.
    This way the Key doesn't "travel" in the URL and is not exposed to everyone.
    """
    def has_permission(self, request, view):
        # Try to extract the key from the Header (more secure)
        api_key = request.headers.get('X-Internal-App-Key')

        # If not in header, check query parameters (backward compatibility)
        if not api_key:
            api_key = request.query_params.get('key')

        return api_key == settings.API_KEY
