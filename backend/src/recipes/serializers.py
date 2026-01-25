from django.db import transaction
from rest_framework import serializers
from django.conf import settings
from .models import Recipes, Ingredients, RecipeIngredients, RecipeLikes, Favorites, RecipeNutrition, Tag
from api_management.models import FoodDataCentralAPI


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    # מאפשר לקבל את שם המרכיב בטקסט במקום ID
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

    # Like and save status
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ['id', 'title', 'description', 'prep_time_minutes', 'cook_time_minutes',
                  'servings', 'status', 'instructions', 'ingredients', 'recipe_ingredients',
                  'tags', 'tag_ids', 'created_at', 'updated_at', 'likes_count', 'is_liked', 'is_saved']
    
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

    # פונקציית עזר פנימית לטיפול במרכיבים כדי לא לחזור על קוד
    def _handle_ingredients(self, recipe, ingredients_data):
        # במקרה של עדכון, נמחק את המרכיבים הישנים וניצור חדשים
        recipe.recipe_ingredients.all().delete()
        
        for item in ingredients_data:
            name = item['ingredient']['name'].lower().strip()
            # השגת המרכיב הכללי או יצירתו
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
            
            # יצירת הקשר בטבלת הצומת
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
        Calculate and save nutritional profile for a recipe based on its ingredients
        """
        try:
            food_api = FoodDataCentralAPI(api_key=settings.API_KEY)
            total_calories = 0.0
            total_protein = 0.0
            total_fat = 0.0
            total_carbs = 0.0
            total_fiber = 0.0
            total_sugars = 0.0
            
            # Iterate through recipe ingredients
            for recipe_ingredient in recipe.recipe_ingredients.all():
                if not recipe_ingredient.fdc_id:
                    continue
                
                # Get nutrition data from API
                nutritions = food_api.search_food_nutritions(str(recipe_ingredient.fdc_id))
                
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
                    'carbs_g': Decimal(str(round(total_carbs, 3))) if total_carbs > 0 else None,
                    'fiber_g': Decimal(str(round(total_fiber, 3))) if total_fiber > 0 else None,
                }
            )
        except Exception as e:
            # Log error but don't fail recipe creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating nutrition for recipe {recipe.id}: {str(e)}")

    @transaction.atomic
    def create(self, validated_data):
        # שליפת המרכיבים מהנתונים (אם קיימים)
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        # שליפת תגיות (אם קיימות)
        tag_ids = validated_data.pop('tag_ids', [])

        # יצירת המתכון (ה-author יועבר מה-View)
        recipe = Recipes.objects.create(**validated_data)

        # הוספת תגיות למתכון
        if tag_ids:
            recipe.tags.set(tag_ids)

        # שימוש בפונקציית העזר ליצירת המרכיבים (אם קיימים)
        if ingredients_data:
            self._handle_ingredients(recipe, ingredients_data)

        # Calculate and save nutrition after ingredients are created
        self._calculate_recipe_nutrition(recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        # שליפת המרכיבים (אם קיימים בבקשה)
        ingredients_data = validated_data.pop('recipe_ingredients', None)
        # שליפת תגיות (אם קיימות בבקשה)
        tag_ids = validated_data.pop('tag_ids', None)

        # עדכון שאר שדות המתכון
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # עדכון תגיות רק אם נשלחו בבקשה
        if tag_ids is not None:
            instance.tags.set(tag_ids)

        # עדכון מרכיבים רק אם נשלחו בבקשה
        if ingredients_data is not None:
            self._handle_ingredients(instance, ingredients_data)
            # Recalculate nutrition when ingredients change
            self._calculate_recipe_nutrition(instance)

        return instance