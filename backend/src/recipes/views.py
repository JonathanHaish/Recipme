from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Recipes
from .serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    # פונקציה שמחזירה את המתכונים של המשתמש ששלח את הבקשה
    @action(detail=False, methods=['get'])
    def my_recipes(self, request):
        # סינון המתכונים כך שרק אלו שה-author שלהם הוא המשתמש המחובר יוחזרו
        user_recipes = Recipes.objects.filter(author=request.user)
        
        # שימוש בסריאליזר כדי להפוך את המתכונים ל-JSON
        serializer = self.get_serializer(user_recipes, many=True)
        return Response(serializer.data)

    
    # פונקציה שמחזירה מתכונים של משתמש ספציפי לפי ID (למשל לצפייה בפרופיל של מישהו אחר)
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[0-9]+)')
    def by_user(self, request, user_id=None):
        user_recipes = Recipes.objects.filter(author_id=user_id, status='published')
        serializer = self.get_serializer(user_recipes, many=True)
        return Response(serializer.data)
    
    
