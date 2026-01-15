from django.db import transaction
from rest_framework import serializers
from .models import Recipes, Ingredients, RecipeIngredients

class RecipeIngredientSerializer(serializers.ModelSerializer):
    # מאפשר לקבל את שם המרכיב בטקסט במקום ID
    ingredient_name = serializers.CharField(source='ingredient.name')

    class Meta:
        model = RecipeIngredients
        fields = ['ingredient_name', 'quantity', 'unit', 'note']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredients')

    class Meta:
        model = Recipes
        fields = ['id', 'title', 'description', 'prep_time_minutes', 'cook_time_minutes', 
                  'servings', 'status', 'instructions', 'ingredients']

    # פונקציית עזר פנימית לטיפול במרכיבים כדי לא לחזור על קוד
    def _handle_ingredients(self, recipe, ingredients_data):
        # במקרה של עדכון, נמחק את המרכיבים הישנים וניצור חדשים
        recipe.recipe_ingredients.all().delete()
        
        for item in ingredients_data:
            name = item['ingredient']['name'].lower().strip()
            # השגת המרכיב הכללי או יצירתו
            ingredient_obj, _ = Ingredients.objects.get_or_create(name=name)
            
            # יצירת הקשר בטבלת הצומת
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient_obj,
                quantity=item['quantity'],
                unit=item.get('unit'),
                note=item.get('note')
            )

    @transaction.atomic
    def create(self, validated_data):
        # שליפת המרכיבים מהנתונים
        ingredients_data = validated_data.pop('recipe_ingredients')
        
        # יצירת המתכון (ה-author יועבר מה-View)
        recipe = Recipes.objects.create(**validated_data)
        
        # שימוש בפונקציית העזר ליצירת המרכיבים
        self._handle_ingredients(recipe, ingredients_data)
        
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        # שליפת המרכיבים (אם קיימים בבקשה)
        ingredients_data = validated_data.pop('recipe_ingredients', None)

        # עדכון שאר שדות המתכון
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # עדכון מרכיבים רק אם נשלחו בבקשה
        if ingredients_data is not None:
            self._handle_ingredients(instance, ingredients_data)
            
        return instance
    


 
        