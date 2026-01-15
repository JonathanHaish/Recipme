from rest_framework import permissions
from django.conf import settings

class IsInternalApp(permissions.BasePermission):
    """
    מאפשר גישה רק אם ה-API Key הפנימי נשלח ב-Header של הבקשה.
    כך ה-Key לא "מטייל" ב-URL וחשוף לעיני כל.
    """
    def has_permission(self, request, view):
        # ננסה להוציא את המפתח מה-Header (יותר מאובטח)
        api_key = request.headers.get('X-Internal-App-Key')
        
        # אם לא ב-header, נבדוק בפרמטרים (תאימות לאחור)
        if not api_key:
            api_key = request.query_params.get('key')
            
        return api_key == settings.API_KEY
