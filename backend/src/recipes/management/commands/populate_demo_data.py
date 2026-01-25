from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from recipes.models import Recipes, Ingredients, RecipeIngredients, Tag, RecipeLikes, Favorites, RecipeImages, RecipeNutrition
from api_management.models import FoodDataCentralAPI
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Populate database with demo users and recipes for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing demo data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing demo data...')
            self.clear_demo_data()

        self.stdout.write('Creating demo users...')
        users = self.create_demo_users()

        self.stdout.write('Creating demo recipes...')
        recipes = self.create_demo_recipes(users)

        self.stdout.write('Calculating nutrition data...')
        self.calculate_nutrition(recipes)

        self.stdout.write('Adding likes and saves...')
        self.add_interactions(users, recipes)

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully created:\n'
            f'  - {len(users)} demo users\n'
            f'  - {len(recipes)} demo recipes\n'
            f'\nDemo users (all with password "demo123"):\n'
            f'  - demo@example.com (regular user)\n'
            f'  - chef@example.com (regular user)\n'
            f'  - foodie@example.com (regular user)\n'
            f'  - admin@example.com (admin user)\n'
        ))

    def clear_demo_data(self):
        """Clear demo users and their recipes"""
        demo_emails = ['demo@example.com', 'chef@example.com', 'foodie@example.com', 'admin@example.com']
        User.objects.filter(email__in=demo_emails).delete()
        self.stdout.write(self.style.WARNING('  Cleared demo data'))

    def create_demo_users(self):
        """Create demo users with different roles"""
        users = []

        # Regular users
        user_data = [
            {'username': 'demo_user', 'email': 'demo@example.com', 'first_name': 'Demo', 'last_name': 'User'},
            {'username': 'chef_john', 'email': 'chef@example.com', 'first_name': 'John', 'last_name': 'Chef'},
            {'username': 'foodie_sarah', 'email': 'foodie@example.com', 'first_name': 'Sarah', 'last_name': 'Foodie'},
        ]

        for data in user_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                self.stdout.write(f'  Created user: {user.email}')
            else:
                self.stdout.write(f'  User already exists: {user.email}')
            users.append(user)

        # Admin user
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin_demo',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('demo123')
            admin.save()
            self.stdout.write(f'  Created admin: {admin.email}')
        else:
            self.stdout.write(f'  Admin already exists: {admin.email}')
        users.append(admin)

        return users

    def create_demo_recipes(self, users):
        """Create demo recipes with tags and ingredients"""
        recipes = []

        # Get or create tags
        tags = {}
        tag_names = ['Vegan', 'Vegetarian', 'Gluten-free', 'High-protein', 'Low-carb', 'Quick & Easy']
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': tag_name.lower().replace(' ', '-').replace('&', 'and')}
            )
            tags[tag_name] = tag

        # Recipe data with realistic ingredients (including FDC IDs for nutrition calculation)
        recipe_data = [
            {
                'title': 'Classic Chicken Caesar Salad',
                'description': 'A fresh and healthy Caesar salad with grilled chicken',
                'instructions': '1. Grill chicken breast until cooked through\n2. Chop romaine lettuce\n3. Mix with Caesar dressing\n4. Top with chicken, croutons, and parmesan\n5. Serve immediately',
                'prep_time': 15,
                'cook_time': 20,
                'servings': 2,
                'tags': ['High-protein'],
                'image_url': 'https://images.unsplash.com/photo-1546793665-c74683f339c1?w=800&h=600&fit=crop',
                'ingredients': [
                    {'name': 'chicken breast', 'quantity': 200, 'fdc_id': 171477},
                    {'name': 'romaine lettuce', 'quantity': 150, 'fdc_id': 169248},
                    {'name': 'parmesan cheese', 'quantity': 30, 'fdc_id': 170899},
                ],
            },
            {
                'title': 'Vegan Buddha Bowl',
                'description': 'Nutritious bowl with quinoa, roasted vegetables, and tahini dressing',
                'instructions': '1. Cook quinoa according to package\n2. Roast sweet potato and chickpeas\n3. Prepare tahini dressing\n4. Arrange in bowl with fresh greens\n5. Drizzle with dressing',
                'prep_time': 20,
                'cook_time': 30,
                'servings': 2,
                'tags': ['Vegan', 'Vegetarian', 'High-protein'],
                'image_url': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&h=600&fit=crop',
                'ingredients': [
                    {'name': 'quinoa', 'quantity': 100, 'fdc_id': 168917},
                    {'name': 'sweet potato', 'quantity': 200, 'fdc_id': 168482},
                    {'name': 'chickpeas', 'quantity': 150, 'fdc_id': 173757},
                    {'name': 'spinach', 'quantity': 100, 'fdc_id': 168462},
                ],
            },
            {
                'title': 'Spaghetti Carbonara',
                'description': 'Classic Italian pasta with eggs, cheese, and pancetta',
                'instructions': '1. Cook spaghetti in salted water\n2. Fry pancetta until crispy\n3. Mix eggs with parmesan\n4. Combine hot pasta with egg mixture\n5. Add pancetta and black pepper',
                'prep_time': 10,
                'cook_time': 15,
                'servings': 4,
                'tags': ['Quick & Easy'],
                'image_url': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800&h=600&fit=crop',
                'ingredients': [
                    {'name': 'spaghetti', 'quantity': 400, 'fdc_id': 169736},
                    {'name': 'eggs', 'quantity': 100, 'fdc_id': 173424},
                    {'name': 'parmesan cheese', 'quantity': 50, 'fdc_id': 170899},
                    {'name': 'bacon', 'quantity': 100, 'fdc_id': 168322},
                ],
            },
            {
                'title': 'Greek Yogurt Parfait',
                'description': 'Healthy breakfast with yogurt, berries, and granola',
                'instructions': '1. Layer Greek yogurt in glass\n2. Add fresh berries\n3. Sprinkle with granola\n4. Drizzle with honey\n5. Serve immediately',
                'prep_time': 5,
                'cook_time': 0,
                'servings': 1,
                'tags': ['Vegetarian', 'High-protein', 'Quick & Easy'],
                'image_url': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&h=600&fit=crop',
                'ingredients': [
                    {'name': 'greek yogurt', 'quantity': 200, 'fdc_id': 170903},
                    {'name': 'blueberries', 'quantity': 100, 'fdc_id': 171711},
                    {'name': 'granola', 'quantity': 50, 'fdc_id': 173230},
                ],
            },
            {
                'title': 'Grilled Salmon with Asparagus',
                'description': 'Healthy omega-3 rich meal with seasonal vegetables',
                'instructions': '1. Season salmon with lemon and herbs\n2. Grill salmon 4-5 minutes per side\n3. Roast asparagus with olive oil\n4. Serve together with lemon wedges',
                'prep_time': 10,
                'cook_time': 15,
                'servings': 2,
                'tags': ['High-protein', 'Low-carb'],
                'image_url': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=800&h=600&fit=crop',
                'ingredients': [
                    {'name': 'salmon', 'quantity': 300, 'fdc_id': 175167},
                    {'name': 'asparagus', 'quantity': 200, 'fdc_id': 168390},
                    {'name': 'olive oil', 'quantity': 15, 'fdc_id': 171413},
                ],
            },
            {
                'title': 'Vegetarian Stir-Fry',
                'description': 'Colorful vegetable stir-fry with tofu and soy sauce',
                'instructions': '1. Press and cube tofu\n2. Stir-fry vegetables in wok\n3. Add tofu and soy sauce\n4. Serve over rice\n5. Garnish with sesame seeds',
                'prep_time': 15,
                'cook_time': 10,
                'servings': 3,
                'tags': ['Vegan', 'Vegetarian', 'Quick & Easy'],
                'image_url': 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800&h=600&fit=crop',
                'ingredients': [
                    {'name': 'tofu', 'quantity': 200, 'fdc_id': 172470},
                    {'name': 'broccoli', 'quantity': 150, 'fdc_id': 170379},
                    {'name': 'bell pepper', 'quantity': 100, 'fdc_id': 170427},
                    {'name': 'soy sauce', 'quantity': 20, 'fdc_id': 172687},
                ],
            },
            {
                'title': 'Avocado Toast with Poached Egg',
                'description': 'Trendy breakfast with healthy fats and protein',
                'instructions': '1. Toast whole grain bread\n2. Mash avocado with lime\n3. Poach eggs\n4. Spread avocado on toast\n5. Top with egg and seasonings',
                'prep_time': 5,
                'cook_time': 10,
                'servings': 2,
                'tags': ['Vegetarian', 'High-protein', 'Quick & Easy'],
                'image_url': 'https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?w=800&h=600&fit=crop',
                'ingredients': [
                    {'name': 'whole wheat bread', 'quantity': 60, 'fdc_id': 172687},
                    {'name': 'avocado', 'quantity': 150, 'fdc_id': 171705},
                    {'name': 'eggs', 'quantity': 100, 'fdc_id': 173424},
                ],
            },
            {
                'title': 'Lentil Soup',
                'description': 'Hearty and nutritious soup perfect for cold days',
                'instructions': '1. Sauté onions and carrots\n2. Add lentils and vegetable broth\n3. Simmer until lentils are tender\n4. Season with cumin and paprika\n5. Serve with crusty bread',
                'prep_time': 10,
                'cook_time': 40,
                'servings': 6,
                'tags': ['Vegan', 'Vegetarian', 'High-protein'],
                'image_url': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800&h=600&fit=crop',
                'ingredients': [
                    {'name': 'lentils', 'quantity': 300, 'fdc_id': 172420},
                    {'name': 'carrots', 'quantity': 150, 'fdc_id': 170393},
                    {'name': 'onion', 'quantity': 100, 'fdc_id': 170000},
                    {'name': 'tomato', 'quantity': 200, 'fdc_id': 170457},
                ],
            },
        ]

        # Create recipes with different authors
        for i, data in enumerate(recipe_data):
            author = users[i % len(users)]  # Distribute recipes among users

            recipe, created = Recipes.objects.get_or_create(
                title=data['title'],
                author=author,
                defaults={
                    'description': data['description'],
                    'instructions': data['instructions'],
                    'prep_time_minutes': data['prep_time'],
                    'cook_time_minutes': data['cook_time'],
                    'servings': data['servings'],
                    'status': 'published',
                }
            )

            if created:
                # Add tags
                for tag_name in data['tags']:
                    if tag_name in tags:
                        recipe.tags.add(tags[tag_name])

                # Add ingredients
                for ing_data in data['ingredients']:
                    ingredient, _ = Ingredients.objects.get_or_create(name=ing_data['name'])
                    RecipeIngredients.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=Decimal(str(ing_data['quantity'])),
                        unit='g',
                        fdc_id=ing_data.get('fdc_id')
                    )

                # Add image if provided
                if 'image_url' in data and data['image_url']:
                    RecipeImages.objects.create(
                        recipe=recipe,
                        image_url=data['image_url'],
                        is_primary=True
                    )

                self.stdout.write(f'  Created recipe: {recipe.title} (by {author.email})')
                recipes.append(recipe)
            else:
                self.stdout.write(f'  Recipe already exists: {recipe.title}')
                recipes.append(recipe)

        return recipes

    def calculate_nutrition(self, recipes):
        """Calculate nutrition data for all recipes"""
        food_api = FoodDataCentralAPI(api_key=settings.API_KEY)

        for recipe in recipes:
            try:
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

                    # Get quantity as float (in grams)
                    try:
                        quantity_g = float(recipe_ingredient.quantity)
                    except (ValueError, TypeError):
                        quantity_g = 0.0

                    # Calculate per 100g basis
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
                self.stdout.write(f'  Calculated nutrition for: {recipe.title}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Failed to calculate nutrition for {recipe.title}: {str(e)}'))

    def add_interactions(self, users, recipes):
        """Add likes and saves to make the demo realistic"""
        # Each user likes and saves some random recipes
        for user in users:
            # Like 3-5 random recipes
            num_likes = random.randint(3, min(5, len(recipes)))
            liked_recipes = random.sample(recipes, num_likes)
            for recipe in liked_recipes:
                RecipeLikes.objects.get_or_create(user=user, recipe=recipe)

            # Save 2-4 random recipes
            num_saves = random.randint(2, min(4, len(recipes)))
            saved_recipes = random.sample(recipes, num_saves)
            for recipe in saved_recipes:
                Favorites.objects.get_or_create(user=user, recipe=recipe)

        self.stdout.write(f'  Added likes and saves for all users')
