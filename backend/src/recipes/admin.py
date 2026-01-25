from django.contrib import admin
from .models import (
    Tag, Recipes, Ingredients, RecipeIngredients,
    Favorites, RecipeImages, RecipeLikes, RecipeNutrition
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at', 'recipes_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'recipes_count']

    def recipes_count(self, obj):
        """Display count of recipes using this tag"""
        return obj.recipes.count()
    recipes_count.short_description = 'Recipe Count'


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


class RecipeImagesInline(admin.TabularInline):
    model = RecipeImages
    extra = 1


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'tags']
    search_fields = ['title', 'description', 'author__username']
    filter_horizontal = ['tags']  # Nice UI for ManyToMany
    inlines = [RecipeIngredientsInline, RecipeImagesInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'description', 'status')
        }),
        ('Recipe Details', {
            'fields': ('prep_time_minutes', 'cook_time_minutes', 'servings', 'instructions')
        }),
        ('Tags', {
            'fields': ('tags',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    list_filter = ['user']
    search_fields = ['user__username', 'recipe__title']


@admin.register(RecipeLikes)
class RecipeLikesAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    list_filter = ['user']
    search_fields = ['user__username', 'recipe__title']


@admin.register(RecipeNutrition)
class RecipeNutritionAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'calories_kcal', 'protein_g', 'fat_g', 'carbs_g', 'fiber_g', 'sugars_g']
    search_fields = ['recipe__title']
    readonly_fields = ['updated_at']
