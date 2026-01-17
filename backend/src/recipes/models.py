from django.db import models
from django.contrib.auth.models import User # שימוש במודל המשתמש המובנה של Django

# ----------------------------------------------------------------------
# טבלת ingredients (תלות של Recipes)
# ----------------------------------------------------------------------
class Ingredients(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ingredients'
        verbose_name_plural = "Ingredients"


    def __str__(self):
        return self.name

# ----------------------------------------------------------------------
# טבלת recipes (הטבלה המרכזית)
# ----------------------------------------------------------------------
class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    prep_time_minutes = models.IntegerField(null=True, blank=True)
    cook_time_minutes = models.IntegerField(null=True, blank=True)
    servings = models.IntegerField(null=True, blank=True)
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    instructions = models.TextField(blank=True, default='')

    # הגדרת יחס רבים לרבים עם Ingredients דרך טבלת הצומת recipe_ingredients
    recipe_ingredients_map = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredients',
        related_name='recipes_using_ingredient'
    )

    class Meta:
        db_table = 'recipes'
        verbose_name_plural = "Recipes"


    
    def __str__(self):
        return self.title

# ----------------------------------------------------------------------
# טבלת recipe_ingredients (טבלת צומת עבור מתכונים ומרכיבים)
# ----------------------------------------------------------------------
class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.PROTECT,
        related_name='ingredient_recipes'
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    unit = models.CharField(max_length=50, null=True, blank=True)
    note = models.CharField(max_length=100, null=True, blank=True)
    fdc_id = models.IntegerField(null=True, blank=True, help_text="Food Data Central API ID for nutrition calculation")

    class Meta:
        db_table = 'recipe_ingredients'
        verbose_name_plural = "Recipe Ingredients"

# ----------------------------------------------------------------------
# טבלת favorites (טבלת צומת עבור משתמשים ומתכונים מועדפים)
# ----------------------------------------------------------------------
class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        db_table = 'favorites'
        verbose_name_plural = "Favorites"
        unique_together = (('user', 'recipe'),)

# ----------------------------------------------------------------------
# טבלת recipe_images (תמונות של מתכונים)
# ----------------------------------------------------------------------
class RecipeImages(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'recipe_images'
        verbose_name_plural = "Recipe Images"

# ----------------------------------------------------------------------
# טבלת recipe_likes (לייקים למתכונים)
# ----------------------------------------------------------------------
class RecipeLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        db_table = 'recipe_likes'
        verbose_name_plural = "Recipe Likes"
        unique_together = (('user', 'recipe'),)

# ----------------------------------------------------------------------
# טבלת recipe_nutrition (נתוני תזונה מחושבים)
# ----------------------------------------------------------------------
class RecipeNutrition(models.Model):
    recipe = models.OneToOneField(Recipes, on_delete=models.CASCADE, primary_key=True, related_name='nutrition')
    calories_kcal = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    protein_g = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    carbs_g = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    fiber_g = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    sodium_mg = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recipe_nutrition'
        verbose_name_plural = "Recipe Nutrition"