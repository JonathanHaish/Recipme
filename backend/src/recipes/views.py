from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from django.db.models import Q, Count
from .models import Recipes, RecipeLikes, Favorites, Tag
from .serializers import RecipeSerializer, TagSerializer
import logging

logger = logging.getLogger(__name__)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing recipe tags.
    Only supports listing and retrieving - tags are managed via admin panel.
    """
    queryset = Tag.objects.filter(is_active=True).order_by('name')
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Log the incoming data for debugging
        logger.info(f"Creating recipe with data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Recipe creation failed: {serializer.errors}")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Update a recipe instance.
        Only allows users to update their own recipes (unless admin).
        """
        instance = self.get_object()
        # Check if user is the author or is admin
        if instance.author != request.user and not (request.user.is_staff or request.user.is_superuser):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own recipes.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a recipe instance.
        Only allows users to update their own recipes (unless admin).
        """
        instance = self.get_object()
        # Check if user is the author or is admin
        if instance.author != request.user and not (request.user.is_staff or request.user.is_superuser):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own recipes.")
        return super().partial_update(request, *args, **kwargs)

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

    # Returns recipes created by the requesting user
    @action(detail=False, methods=['get'])
    def my_recipes(self, request):
        # Filter recipes to only those where the author is the logged-in user
        user_recipes = Recipes.objects.filter(author=request.user)

        # Use serializer to convert recipes to JSON
        serializer = self.get_serializer(user_recipes, many=True)
        return Response(serializer.data)


    # Returns recipes by a specific user ID (e.g., for viewing someone else's profile)
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
    
    # Filter recipes by tags with OR/AND logic
    @action(detail=False, methods=['get'])
    def filter_by_tags(self, request):
        """
        Filter recipes by multiple tags.
        Query params:
        - tag_ids: comma-separated list of tag IDs (e.g., "1,2,3")
        - match: "any" (OR logic, default) or "all" (AND logic)

        Examples:
        - /recipes/filter_by_tags/?tag_ids=1,2&match=any  # Recipes with tag 1 OR tag 2
        - /recipes/filter_by_tags/?tag_ids=1,2&match=all  # Recipes with tag 1 AND tag 2
        """
        tag_ids_str = request.query_params.get('tag_ids', '').strip()
        match_mode = request.query_params.get('match', 'any').lower()

        if not tag_ids_str:
            return Response([])

        try:
            tag_ids = [int(tid.strip()) for tid in tag_ids_str.split(',') if tid.strip()]
        except ValueError:
            return Response({'error': 'Invalid tag_ids format'}, status=400)

        if not tag_ids:
            return Response([])

        # Start with user's recipes
        recipes = Recipes.objects.filter(author=request.user)

        if match_mode == 'all':
            # AND logic - recipe must have ALL specified tags
            for tag_id in tag_ids:
                recipes = recipes.filter(tags__id=tag_id)
            recipes = recipes.distinct()
        else:
            # OR logic (default) - recipe must have ANY of the specified tags
            recipes = recipes.filter(tags__id__in=tag_ids).distinct()

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
    