from django.db import transaction
from rest_framework import serializers
from django.conf import settings
from django.core.files.base import ContentFile
import base64
import uuid
from .models import Recipes, Ingredients, RecipeIngredients, RecipeLikes, Favorites, RecipeNutrition, Tag, RecipeImages
from api_management.models import FoodDataCentralAPI


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description']

class RecipeImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = RecipeImages
        fields = ['id', 'image', 'image_url', 'is_primary']
        read_only_fields = ['id']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return obj.image_url

class RecipeNutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeNutrition
        fields = ['calories_kcal', 'protein_g', 'fat_g', 'carbs_g', 'fiber_g', 'sugars_g', 'updated_at']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    # Allows getting the ingredient name as text instead of ID
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)

    class Meta:
        model = RecipeIngredients
        fields = ['ingredient_name', 'quantity', 'unit', 'note']

# Serializer for writing ingredient data (input)
class RecipeIngredientWriteSerializer(serializers.Serializer):
    ingredient = serializers.DictField(child=serializers.CharField())
    quantity = serializers.CharField()
    unit = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    note = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    fdc_id = serializers.IntegerField(required=False, allow_null=True)

class RecipeSerializer(serializers.ModelSerializer):
    # For reading - use nested serializer
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients', read_only=True)
    # For writing - accept ingredients in the request
    recipe_ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True, required=False)

    # Tags - nested for reading, IDs for writing
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    # Images - nested for reading
    images = RecipeImageSerializer(many=True, read_only=True)
    # Primary image URL for easy access
    image_url = serializers.SerializerMethodField()
    # For writing - accept base64 image data
    image = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    # Like and save status
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    # Nutrition data
    nutrition = RecipeNutritionSerializer(read_only=True)

    # Author ID (read-only)
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Recipes
        fields = ['id', 'author', 'title', 'description', 'prep_time_minutes', 'cook_time_minutes',
                  'servings', 'status', 'instructions', 'ingredients', 'recipe_ingredients',
                  'tags', 'tag_ids', 'created_at', 'updated_at', 'likes_count', 'is_liked', 'is_saved',
                  'nutrition', 'images', 'image_url', 'image', 'youtube_url']
    
    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return RecipeLikes.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorites.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_image_url(self, obj):
        """Get the primary image URL or the first image"""
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = obj.images.first()

        if primary_image:
            # Check for uploaded image file first
            if primary_image.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(primary_image.image.url)
                return primary_image.image.url
            # Fall back to image_url for external URLs
            elif primary_image.image_url:
                return primary_image.image_url

        return None

    def _handle_image(self, recipe, image_data):
        """Handle base64 image upload"""
        if not image_data:
            return

        try:
            # Check if it's a base64 string
            if image_data.startswith('data:image'):
                # Extract the base64 data
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]

                # Decode base64 string
                data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')

                # Delete old images for this recipe
                recipe.images.all().delete()

                # Create new image
                RecipeImages.objects.create(
                    recipe=recipe,
                    image=data,
                    is_primary=True
                )
        except Exception as e:
            # Log error but don't fail recipe creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error handling image for recipe {recipe.id}: {str(e)}")

    # Internal helper function to handle ingredients without code duplication
    def _handle_ingredients(self, recipe, ingredients_data):
        # In case of update, delete old ingredients and create new ones
        recipe.recipe_ingredients.all().delete()

        for item in ingredients_data:
            name = item['ingredient']['name'].lower().strip()
            # Get or create the ingredient object
            ingredient_obj, _ = Ingredients.objects.get_or_create(name=name)
            
            # Convert quantity string to Decimal if needed
            quantity = item['quantity']
            if isinstance(quantity, str):
                # Try to convert string to decimal, default to 0 if invalid
                try:
                    from decimal import Decimal
                    quantity = Decimal(quantity)
                except (ValueError, TypeError):
                    quantity = Decimal('0')
            
            # Get fdc_id from ingredient dict if available
            fdc_id = None
            if 'ingredient' in item and isinstance(item['ingredient'], dict):
                # Check if fdc_id is in the ingredient dict or if 'id' is provided separately
                fdc_id = item['ingredient'].get('id') or item.get('fdc_id')
                if fdc_id:
                    try:
                        fdc_id = int(fdc_id)
                    except (ValueError, TypeError):
                        fdc_id = None

            # Create the relationship in the junction table
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient_obj,
                quantity=quantity,
                unit=item.get('unit') or None,
                note=item.get('note') or None,
                fdc_id=fdc_id
            )

    def _calculate_recipe_nutrition(self, recipe):
        """
        Calculate and save nutritional profile for a recipe based on its ingredients.
        Uses batch fetching to get all nutrition data concurrently.
        """
        try:
            food_api = FoodDataCentralAPI(api_key=settings.API_KEY)
            total_calories = 0.0
            total_protein = 0.0
            total_fat = 0.0
            total_carbs = 0.0
            total_fiber = 0.0
            total_sugars = 0.0

            # Collect all fdc_ids and ingredients with fdc_id
            ingredients_with_fdc = []
            fdc_ids = []

            for recipe_ingredient in recipe.recipe_ingredients.all():
                if recipe_ingredient.fdc_id:
                    ingredients_with_fdc.append(recipe_ingredient)
                    fdc_ids.append(str(recipe_ingredient.fdc_id))

            # Fetch all nutrition data concurrently in one batch
            if fdc_ids:
                nutrition_map = food_api.search_food_nutritions_batch(fdc_ids)
            else:
                nutrition_map = {}

            # Process each ingredient with its nutrition data
            for recipe_ingredient in ingredients_with_fdc:
                fdc_id = str(recipe_ingredient.fdc_id)
                nutritions = nutrition_map.get(fdc_id, {})

                if not nutritions:
                    continue

                # Get quantity as float (in grams, assuming quantity is in grams)
                try:
                    quantity_g = float(recipe_ingredient.quantity)
                except (ValueError, TypeError):
                    quantity_g = 0.0

                # Calculate per 100g basis (API returns per 100g typically)
                multiplier = quantity_g / 100.0 if quantity_g > 0 else 0

                # Sum up nutrients
                if 'calories' in nutritions and nutritions['calories'].get('value'):
                    total_calories += nutritions['calories']['value'] * multiplier
                if 'protein' in nutritions and nutritions['protein'].get('value'):
                    total_protein += nutritions['protein']['value'] * multiplier
                if 'fat' in nutritions and nutritions['fat'].get('value'):
                    total_fat += nutritions['fat']['value'] * multiplier
                if 'carbohydrates' in nutritions and nutritions['carbohydrates'].get('value'):
                    total_carbs += nutritions['carbohydrates']['value'] * multiplier
                if 'fiber' in nutritions and nutritions['fiber'].get('value'):
                    total_fiber += nutritions['fiber']['value'] * multiplier
                if 'sugars' in nutritions and nutritions['sugars'].get('value'):
                    total_sugars += nutritions['sugars']['value'] * multiplier
            
            # Save or update RecipeNutrition
            from decimal import Decimal
            RecipeNutrition.objects.update_or_create(
                recipe=recipe,
                defaults={
                    'calories_kcal': Decimal(str(round(total_calories, 3))) if total_calories > 0 else None,
                    'protein_g': Decimal(str(round(total_protein, 3))) if total_protein > 0 else None,
                    'fat_g': Decimal(str(round(total_fat, 3))) if total_fat > 0 else None,
                    'carbs_g': Decimal(str(round(total_carbs, 3))) if total_carbs > 0 else None,
                    'fiber_g': Decimal(str(round(total_fiber, 3))) if total_fiber > 0 else None,
                    'sugars_g': Decimal(str(round(total_sugars, 3))) if total_sugars > 0 else None,
                }
            )
        except Exception as e:
            # Log error but don't fail recipe creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating nutrition for recipe {recipe.id}: {str(e)}")

    @transaction.atomic
    def create(self, validated_data):
        # Extract ingredients from data (if they exist)
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        # Extract tags (if they exist)
        tag_ids = validated_data.pop('tag_ids', [])
        # Extract image (if it exists)
        image_data = validated_data.pop('image', None)

        # Create the recipe (author will be passed from the View)
        recipe = Recipes.objects.create(**validated_data)

        # Add tags to the recipe
        if tag_ids:
            recipe.tags.set(tag_ids)

        # Use helper function to create ingredients (if they exist)
        if ingredients_data:
            self._handle_ingredients(recipe, ingredients_data)

        # Handle image upload
        if image_data:
            self._handle_image(recipe, image_data)

        # Calculate and save nutrition after ingredients are created
        self._calculate_recipe_nutrition(recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        # Extract ingredients (if they exist in the request)
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        # Extract tags (if they exist in the request)
        tag_ids = validated_data.pop('tag_ids', None)
        # Extract image (if it exists in the request)
        image_data = validated_data.pop('image', None)

        # Update other recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tags only if they were sent in the request
        if tag_ids is not None:
            instance.tags.set(tag_ids)

        # Handle image upload if provided
        if image_data is not None:
            self._handle_image(instance, image_data)

        # Update ingredients only if they were sent in the request
        if ingredients_data is not None:
            self._handle_ingredients(instance, ingredients_data)
            # Recalculate nutrition when ingredients change
            self._calculate_recipe_nutrition(instance)

        return instance