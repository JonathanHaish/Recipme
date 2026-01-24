from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from django.db.models import Q
from .models import Recipes, RecipeLikes, Favorites
from .serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Now we receive JSON with image_url, not FormData with image file
        data = request.data
        serializer = self.get_serializer(data=data, context={'request': request})
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            from rest_framework import status
            from rest_framework.response import Response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        # Now we receive JSON with image_url, not FormData with image file
        data = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a recipe instance.
        Only allows users to delete their own recipes.
        """
        instance = self.get_object()
        # Check if user is the author or is admin
        if instance.author != request.user and not (request.user.is_staff or request.user.is_superuser):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own recipes.")
        self.perform_destroy(instance)
        return Response(status=204)

    def perform_destroy(self, instance):
        """
        Perform the actual deletion of the recipe instance.
        This also handles cascade deletion of related objects.
        """
        instance.delete()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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
    
    # Search recipes by title or description
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response([])
        
        # Search in title and description
        recipes = Recipes.objects.filter(
            author=request.user
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)
    
    # Filter recipes by type (description)
    @action(detail=False, methods=['get'])
    def filter_by_type(self, request):
        recipe_type = request.query_params.get('type', '').strip()
        if not recipe_type:
            return Response([])
        
        recipes = Recipes.objects.filter(author=request.user, description__iexact=recipe_type)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)
    
    # Get top 10 recipes by likes (placeholder - requires likes model)
    @action(detail=False, methods=['get'])
    def top_liked(self, request):
        # For now, return user's recipes ordered by created_at
        # TODO: Implement actual likes system
        recipes = Recipes.objects.filter(author=request.user).order_by('-created_at')[:10]
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)
    
    # Get user's saved recipes
    @action(detail=False, methods=['get'])
    def saved(self, request):
        saved_recipe_ids = Favorites.objects.filter(user=request.user).values_list('recipe_id', flat=True)
        recipes = Recipes.objects.filter(id__in=saved_recipe_ids)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)
    
    # Toggle like on a recipe
    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        recipe = self.get_object()
        like, created = RecipeLikes.objects.get_or_create(user=request.user, recipe=recipe)
        
        if not created:
            # Like already exists, remove it
            like.delete()
            return Response({'liked': False, 'likes_count': recipe.likes.count()})
        
        return Response({'liked': True, 'likes_count': recipe.likes.count()})
    
    # Toggle save on a recipe
    @action(detail=True, methods=['post'])
    def toggle_save(self, request, pk=None):
        recipe = self.get_object()
        favorite, created = Favorites.objects.get_or_create(user=request.user, recipe=recipe)
        
        if not created:
            # Favorite already exists, remove it
            favorite.delete()
            return Response({'saved': False})
        
        return Response({'saved': True})
    