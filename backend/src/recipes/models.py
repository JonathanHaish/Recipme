from django.db import models
from django.contrib.auth.models import User  # Using Django's built-in User model

# ----------------------------------------------------------------------
# recipe_tags table (tags for recipes)
# ----------------------------------------------------------------------
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)  # Explicit index for slug lookups
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)  # Index for filtering active tags

    class Meta:
        db_table = 'recipe_tags'
        verbose_name_plural = "Recipe Tags"
        ordering = ['name']

    def __str__(self):
        return self.name

# ----------------------------------------------------------------------
# ingredients table (dependency of Recipes)
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
# recipes table (the main table)
# ----------------------------------------------------------------------
class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        db_index=True  # Index for filtering by author
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)  # Index for filtering by status

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Index for ordering by date
    updated_at = models.DateTimeField(auto_now=True)
    instructions = models.TextField(blank=True, default='')

    # Many-to-many relationship with Tags
    tags = models.ManyToManyField('Tag', related_name='recipes', blank=True)

    # Many-to-many relationship with Ingredients through the junction table recipe_ingredients
    recipe_ingredients_map = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredients',
        related_name='recipes_using_ingredient'
    )

    class Meta:
        db_table = 'recipes'
        verbose_name_plural = "Recipes"
        ordering = ['-created_at']  # Newest recipes first


    
    def __str__(self):
        return self.title

# ----------------------------------------------------------------------
# recipe_ingredients table (junction table for recipes and ingredients)
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
# favorites table (junction table for users and favorite recipes)
# ----------------------------------------------------------------------
class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        db_table = 'favorites'
        verbose_name_plural = "Favorites"
        unique_together = (('user', 'recipe'),)

# ----------------------------------------------------------------------
# recipe_images table (images for recipes)
# ----------------------------------------------------------------------
class RecipeImages(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='recipe_images/', null=True, blank=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)  # For external URLs or fallback
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'recipe_images'
        verbose_name_plural = "Recipe Images"

# ----------------------------------------------------------------------
# recipe_likes table (likes for recipes)
# ----------------------------------------------------------------------
class RecipeLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        db_table = 'recipe_likes'
        verbose_name_plural = "Recipe Likes"
        unique_together = (('user', 'recipe'),)

# ----------------------------------------------------------------------
# recipe_nutrition table (calculated nutrition data)
# ----------------------------------------------------------------------
class RecipeNutrition(models.Model):
    recipe = models.OneToOneField(Recipes, on_delete=models.CASCADE, primary_key=True, related_name='nutrition')
    calories_kcal = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    protein_g = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    fat_g = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    carbs_g = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    fiber_g = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    sugars_g = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recipe_nutrition'
        verbose_name_plural = "Recipe Nutrition"