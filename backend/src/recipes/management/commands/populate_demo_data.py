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
                'image_url': 'https://picsum.photos/seed/caesar/800/600',
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
                'image_url': 'https://picsum.photos/seed/buddha/800/600',
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
                'image_url': 'https://picsum.photos/seed/carbonara/800/600',
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
                'image_url': 'https://picsum.photos/seed/parfait/800/600',
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
                'image_url': 'https://picsum.photos/seed/salmon/800/600',
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
                'image_url': 'https://picsum.photos/seed/stirfry/800/600',
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
                'image_url': 'https://picsum.photos/seed/avocado/800/600',
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
                'image_url': 'https://picsum.photos/seed/lentils/800/600',
                'ingredients': [
                    {'name': 'lentils', 'quantity': 300, 'fdc_id': 172420},
                    {'name': 'carrots', 'quantity': 150, 'fdc_id': 170393},
                    {'name': 'onion', 'quantity': 100, 'fdc_id': 170000},
                    {'name': 'tomato', 'quantity': 200, 'fdc_id': 170457},
                ],
            },
            # New Breakfast Recipes
            {
                'title': 'Fluffy Pancakes',
                'description': 'Classic American pancakes that are light and fluffy',
                'instructions': '1. Mix flour, sugar, baking powder, and salt\n2. Whisk eggs, milk, and melted butter\n3. Combine wet and dry ingredients\n4. Cook on griddle until bubbles form\n5. Flip and cook until golden',
                'prep_time': 10,
                'cook_time': 15,
                'servings': 4,
                'tags': ['Vegetarian', 'Quick & Easy'],
                'image_url': 'https://picsum.photos/seed/pancakes/800/600',
                'youtube_url': 'https://www.youtube.com/watch?v=mhDJNfV7hjk',
                'ingredients': [
                    {'name': 'all-purpose flour', 'quantity': 200, 'fdc_id': 169761},
                    {'name': 'eggs', 'quantity': 100, 'fdc_id': 173424},
                    {'name': 'milk', 'quantity': 250, 'fdc_id': 171265},
                ],
            },
            {
                'title': 'Overnight Oats',
                'description': 'No-cook breakfast oats with fruit and nuts',
                'instructions': '1. Mix oats with milk in jar\n2. Add chia seeds and honey\n3. Refrigerate overnight\n4. Top with berries and nuts\n5. Enjoy cold or warmed',
                'prep_time': 5,
                'cook_time': 0,
                'servings': 1,
                'tags': ['Vegetarian', 'High-protein', 'Quick & Easy'],
                'image_url': 'https://picsum.photos/seed/oats/800/600',
                'youtube_url': 'https://www.youtube.com/watch?v=mhDJNfV7hjk',
                'ingredients': [
                    {'name': 'oats', 'quantity': 80, 'fdc_id': 169705},
                    {'name': 'milk', 'quantity': 200, 'fdc_id': 171265},
                    {'name': 'blueberries', 'quantity': 50, 'fdc_id': 171711},
                ],
            },
            {
                'title': 'Breakfast Burrito',
                'description': 'Hearty breakfast wrap with eggs, cheese, and vegetables',
                'instructions': '1. Scramble eggs with salt and pepper\n2. Warm tortilla\n3. Add eggs, cheese, and salsa\n4. Roll into burrito\n5. Serve with sour cream',
                'prep_time': 10,
                'cook_time': 10,
                'servings': 2,
                'tags': ['Vegetarian', 'High-protein'],
                'image_url': 'https://picsum.photos/seed/burrito/800/600',
                'ingredients': [
                    {'name': 'eggs', 'quantity': 150, 'fdc_id': 173424},
                    {'name': 'cheddar cheese', 'quantity': 50, 'fdc_id': 173417},
                    {'name': 'tortilla', 'quantity': 100, 'fdc_id': 172687},
                ],
            },
            # New Lunch Recipes
            {
                'title': 'Caprese Sandwich',
                'description': 'Italian-style sandwich with mozzarella, tomato, and basil',
                'instructions': '1. Slice ciabatta bread\n2. Layer mozzarella and tomato slices\n3. Add fresh basil leaves\n4. Drizzle with balsamic and olive oil\n5. Season with salt and pepper',
                'prep_time': 10,
                'cook_time': 0,
                'servings': 2,
                'tags': ['Vegetarian', 'Quick & Easy'],
                'image_url': 'https://picsum.photos/seed/caprese/800/600',
                'youtube_url': 'https://www.youtube.com/watch?v=mhDJNfV7hjk',
                'ingredients': [
                    {'name': 'mozzarella cheese', 'quantity': 150, 'fdc_id': 173418},
                    {'name': 'tomato', 'quantity': 200, 'fdc_id': 170457},
                    {'name': 'bread', 'quantity': 100, 'fdc_id': 172687},
                ],
            },
            {
                'title': 'Mediterranean Quinoa Bowl',
                'description': 'Fresh bowl with quinoa, feta, olives, and cucumber',
                'instructions': '1. Cook quinoa according to package\n2. Dice cucumber and tomatoes\n3. Mix with olives and feta\n4. Dress with lemon and olive oil\n5. Season with herbs',
                'prep_time': 15,
                'cook_time': 20,
                'servings': 3,
                'tags': ['Vegetarian', 'Gluten-free'],
                'image_url': 'https://picsum.photos/seed/quinoa/800/600',
                'ingredients': [
                    {'name': 'quinoa', 'quantity': 150, 'fdc_id': 168917},
                    {'name': 'feta cheese', 'quantity': 80, 'fdc_id': 173420},
                    {'name': 'cucumber', 'quantity': 150, 'fdc_id': 168409},
                ],
            },
            {
                'title': 'Thai Peanut Noodles',
                'description': 'Spicy noodles with vegetables and peanut sauce',
                'instructions': '1. Cook rice noodles\n2. Stir-fry vegetables\n3. Mix peanut butter with soy sauce and lime\n4. Toss noodles with sauce and vegetables\n5. Garnish with peanuts and cilantro',
                'prep_time': 15,
                'cook_time': 10,
                'servings': 4,
                'tags': ['Vegan', 'Vegetarian'],
                'image_url': 'https://picsum.photos/seed/noodles/800/600',
                'ingredients': [
                    {'name': 'rice noodles', 'quantity': 200, 'fdc_id': 169738},
                    {'name': 'peanut butter', 'quantity': 60, 'fdc_id': 174262},
                    {'name': 'bell pepper', 'quantity': 100, 'fdc_id': 170427},
                ],
            },
            # New Dinner Recipes
            {
                'title': 'Beef Tacos',
                'description': 'Classic Mexican tacos with seasoned ground beef',
                'instructions': '1. Brown ground beef with taco seasoning\n2. Warm taco shells\n3. Fill with beef and toppings\n4. Add lettuce, cheese, and salsa\n5. Serve with lime wedges',
                'prep_time': 10,
                'cook_time': 15,
                'servings': 4,
                'tags': ['High-protein', 'Quick & Easy'],
                'image_url': 'https://picsum.photos/seed/tacos/800/600',
                'youtube_url': 'https://www.youtube.com/watch?v=mhDJNfV7hjk',
                'ingredients': [
                    {'name': 'ground beef', 'quantity': 400, 'fdc_id': 174032},
                    {'name': 'lettuce', 'quantity': 100, 'fdc_id': 169248},
                    {'name': 'cheddar cheese', 'quantity': 80, 'fdc_id': 173417},
                ],
            },
            {
                'title': 'Chicken Tikka Masala',
                'description': 'Creamy Indian curry with tender chicken pieces',
                'instructions': '1. Marinate chicken in yogurt and spices\n2. Grill or pan-fry chicken\n3. Make tomato-cream sauce with spices\n4. Add chicken to sauce and simmer\n5. Serve with rice and naan',
                'prep_time': 30,
                'cook_time': 40,
                'servings': 6,
                'tags': ['High-protein', 'Gluten-free'],
                'image_url': 'https://picsum.photos/seed/tikka/800/600',
                'youtube_url': 'https://www.youtube.com/watch?v=mhDJNfV7hjk',
                'ingredients': [
                    {'name': 'chicken breast', 'quantity': 600, 'fdc_id': 171477},
                    {'name': 'greek yogurt', 'quantity': 150, 'fdc_id': 170903},
                    {'name': 'tomato', 'quantity': 300, 'fdc_id': 170457},
                ],
            },
            {
                'title': 'Mushroom Risotto',
                'description': 'Creamy Italian rice dish with mushrooms',
                'instructions': '1. Sauté mushrooms and set aside\n2. Toast arborio rice in butter\n3. Gradually add warm broth, stirring constantly\n4. Add mushrooms and parmesan\n5. Season and serve immediately',
                'prep_time': 10,
                'cook_time': 30,
                'servings': 4,
                'tags': ['Vegetarian', 'Gluten-free'],
                'image_url': 'https://picsum.photos/seed/risotto/800/600',
                'ingredients': [
                    {'name': 'arborio rice', 'quantity': 300, 'fdc_id': 169756},
                    {'name': 'mushrooms', 'quantity': 250, 'fdc_id': 169242},
                    {'name': 'parmesan cheese', 'quantity': 60, 'fdc_id': 170899},
                ],
            },
            # New Dessert Recipes
            {
                'title': 'Chocolate Chip Cookies',
                'description': 'Classic homemade cookies with chocolate chips',
                'instructions': '1. Cream butter and sugars\n2. Add eggs and vanilla\n3. Mix in flour and baking soda\n4. Fold in chocolate chips\n5. Bake until golden',
                'prep_time': 15,
                'cook_time': 12,
                'servings': 24,
                'tags': ['Vegetarian'],
                'image_url': 'https://picsum.photos/seed/cookies/800/600',
                'youtube_url': 'https://www.youtube.com/watch?v=mhDJNfV7hjk',
                'ingredients': [
                    {'name': 'all-purpose flour', 'quantity': 280, 'fdc_id': 169761},
                    {'name': 'butter', 'quantity': 200, 'fdc_id': 173430},
                    {'name': 'chocolate chips', 'quantity': 200, 'fdc_id': 170273},
                ],
            },
            {
                'title': 'Banana Bread',
                'description': 'Moist and sweet bread made with ripe bananas',
                'instructions': '1. Mash ripe bananas\n2. Mix with melted butter and sugar\n3. Add eggs and vanilla\n4. Fold in flour and baking soda\n5. Bake until golden',
                'prep_time': 15,
                'cook_time': 60,
                'servings': 8,
                'tags': ['Vegetarian'],
                'image_url': 'https://picsum.photos/seed/banana/800/600',
                'youtube_url': 'https://www.youtube.com/watch?v=mhDJNfV7hjk',
                'ingredients': [
                    {'name': 'bananas', 'quantity': 400, 'fdc_id': 173944},
                    {'name': 'all-purpose flour', 'quantity': 250, 'fdc_id': 169761},
                    {'name': 'butter', 'quantity': 100, 'fdc_id': 173430},
                ],
            },
            {
                'title': 'Lemon Bars',
                'description': 'Tangy lemon dessert bars with shortbread crust',
                'instructions': '1. Make shortbread crust and bake\n2. Whisk lemon juice, eggs, and sugar\n3. Pour over crust\n4. Bake until set\n5. Cool and dust with powdered sugar',
                'prep_time': 20,
                'cook_time': 45,
                'servings': 16,
                'tags': ['Vegetarian'],
                'image_url': 'https://picsum.photos/seed/lemon/800/600',
                'ingredients': [
                    {'name': 'all-purpose flour', 'quantity': 200, 'fdc_id': 169761},
                    {'name': 'lemons', 'quantity': 150, 'fdc_id': 167747},
                    {'name': 'eggs', 'quantity': 150, 'fdc_id': 173424},
                ],
            },
            # New Snack Recipes
            {
                'title': 'Homemade Hummus',
                'description': 'Creamy Middle Eastern chickpea dip',
                'instructions': '1. Blend chickpeas until smooth\n2. Add tahini, lemon, and garlic\n3. Drizzle in olive oil while blending\n4. Season with salt and cumin\n5. Serve with vegetables or pita',
                'prep_time': 10,
                'cook_time': 0,
                'servings': 8,
                'tags': ['Vegan', 'Vegetarian', 'Gluten-free'],
                'image_url': 'https://picsum.photos/seed/hummus/800/600',
                'youtube_url': 'https://www.youtube.com/watch?v=mhDJNfV7hjk',
                'ingredients': [
                    {'name': 'chickpeas', 'quantity': 400, 'fdc_id': 173757},
                    {'name': 'tahini', 'quantity': 80, 'fdc_id': 172470},
                    {'name': 'olive oil', 'quantity': 30, 'fdc_id': 171413},
                ],
            },
            {
                'title': 'Energy Balls',
                'description': 'No-bake protein-packed snack balls',
                'instructions': '1. Process dates and nuts\n2. Add oats and honey\n3. Mix until sticky\n4. Roll into balls\n5. Refrigerate until firm',
                'prep_time': 15,
                'cook_time': 0,
                'servings': 12,
                'tags': ['Vegan', 'Vegetarian', 'High-protein'],
                'image_url': 'https://images.unsplash.com/photo-1623428187969-5da2dcea5ebf?w=800&h=600&fit=crop',
                'ingredients': [
                    {'name': 'dates', 'quantity': 200, 'fdc_id': 168191},
                    {'name': 'oats', 'quantity': 100, 'fdc_id': 169705},
                    {'name': 'almonds', 'quantity': 100, 'fdc_id': 170567},
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
                    'youtube_url': data.get('youtube_url'),
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
        """Calculate nutrition data for all recipes with proper connection cleanup"""
        # Use context manager to ensure connections are closed
        with FoodDataCentralAPI(api_key=settings.API_KEY) as food_api:
            # Collect all unique fdc_ids from all recipes
            all_fdc_ids = set()
            for recipe in recipes:
                for recipe_ingredient in recipe.recipe_ingredients.all():
                    if recipe_ingredient.fdc_id:
                        all_fdc_ids.add(str(recipe_ingredient.fdc_id))

            # Fetch all nutrition data in batch
            self.stdout.write(f'  Fetching nutrition data for {len(all_fdc_ids)} unique ingredients...')
            nutrition_map = food_api.search_food_nutritions_batch(list(all_fdc_ids))
            self.stdout.write(self.style.SUCCESS(f'  Fetched nutrition data for {len(nutrition_map)} ingredients'))

            # Now process each recipe using the pre-fetched data
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

                        # Get nutrition data from pre-fetched map
                        fdc_id = str(recipe_ingredient.fdc_id)
                        nutritions = nutrition_map.get(fdc_id, {})

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
