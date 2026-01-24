from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from django.db.models import Q, Case, When, IntegerField
from .models import Recipes, RecipeLikes, Favorites
from .serializers import RecipeSerializer
from profiles.models import UserProfile, Goal, DietType


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Override to return all published recipes for list view.
        This allows users to see all public recipes, not just their own.
        """
        # For list action, return all published recipes
        if self.action == 'list':
            return Recipes.objects.filter(status='published')
        # For other actions, use default queryset
        return Recipes.objects.all()

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
    
    @action(detail=False, methods=['get'])
    def personalized(self, request):
        """
        Get all PUBLIC recipes ordered by user's profile preferences.
        Recipes matching user's diet preference appear first.
        Recipes matching user's goals appear next.
        Then all other public recipes.
        """
        # Get all PUBLIC recipes (published status)
        all_recipes = Recipes.objects.filter(status='published')
        
        # Get user profile
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            # If no profile, return all public recipes in default order
            all_recipes = all_recipes.order_by('-created_at')
            serializer = self.get_serializer(all_recipes, many=True)
            return Response(serializer.data)
        
        # Get user's diet preference
        user_diet = user_profile.diet
        user_goals = user_profile.goals.all()
        
        # Create a mapping of goal codes to recipe type keywords
        goal_keywords = {
            'weight_loss': ['low calorie', 'low fat', 'weight loss', 'diet', 'light'],
            'weight_gain': ['high calorie', 'high protein', 'weight gain', 'bulk'],
            'muscle_gain': ['high protein', 'muscle', 'protein', 'strength', 'fitness'],
            'maintain_weight': ['balanced', 'maintain', 'healthy'],
            'improve_health': ['healthy', 'nutritious', 'wellness', 'health'],
            'increase_energy': ['energy', 'energizing', 'boost', 'vitality'],
            'better_nutrition': ['nutritious', 'healthy', 'balanced', 'nutrition'],
            'meal_prep': ['meal prep', 'prep', 'batch', 'make ahead'],
            'healthy_eating': ['healthy', 'nutritious', 'clean', 'whole'],
            'build_strength': ['high protein', 'strength', 'muscle', 'fitness'],
            'improve_digestion': ['digestive', 'fiber', 'probiotic', 'gut health'],
            'heart_health': ['heart healthy', 'cardio', 'low sodium', 'omega'],
            'diabetes_management': ['low sugar', 'diabetic', 'low glycemic', 'blood sugar'],
            'reduce_inflammation': ['anti-inflammatory', 'turmeric', 'ginger', 'omega'],
            'boost_immunity': ['immune', 'vitamin c', 'antioxidant', 'immunity'],
            'improve_skin': ['skin', 'collagen', 'antioxidant', 'vitamin e'],
            'better_sleep': ['sleep', 'tryptophan', 'melatonin', 'relaxing'],
            'sports_performance': ['performance', 'sports', 'athletic', 'recovery'],
        }
        
        # Build ordering conditions
        when_conditions = []
        order_value = 0
        
        # First priority: Recipes matching user's diet preference
        if user_diet:
            diet_name_lower = user_diet.name.lower()
            diet_code_lower = user_diet.code.lower()
            # Normalize diet name for matching (handle variations)
            diet_variations = [diet_name_lower, diet_code_lower]
            # Add common variations (e.g., "lactose-free" vs "lactose free")
            if '-' in diet_name_lower:
                diet_variations.append(diet_name_lower.replace('-', ' '))
            if ' ' in diet_name_lower:
                diet_variations.append(diet_name_lower.replace(' ', '-'))
            
            # Check if recipe description contains diet name, code, or variations
            diet_q = Q()
            for variation in diet_variations:
                diet_q |= Q(description__icontains=variation) | Q(title__icontains=variation)
            
            when_conditions.append(
                When(diet_q, then=order_value)
            )
            order_value += 1
        
        # Second priority: Recipes matching user's goals
        goal_keywords_list = []
        for goal in user_goals:
            if goal.code in goal_keywords:
                goal_keywords_list.extend(goal_keywords[goal.code])
        
        if goal_keywords_list:
            # Create Q object for goal matching
            goal_q = Q()
            for keyword in goal_keywords_list:
                goal_q |= Q(description__icontains=keyword) | Q(title__icontains=keyword)
            
            when_conditions.append(
                When(goal_q, then=order_value)
            )
            order_value += 1
        
        # Default: All other recipes
        when_conditions.append(
            When(pk__isnull=False, then=order_value)
        )
        
        # Apply ordering
        if when_conditions:
            all_recipes = all_recipes.annotate(
                match_priority=Case(
                    *when_conditions,
                    default=order_value,
                    output_field=IntegerField()
                )
            ).order_by('match_priority', '-created_at')
        else:
            all_recipes = all_recipes.order_by('-created_at')
        
        serializer = self.get_serializer(all_recipes, many=True)
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
    