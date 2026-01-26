from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import Recipes, Tag, Ingredients, RecipeIngredients, RecipeLikes, Favorites


class RecipeModelTests(TestCase):
    """Test Recipe model functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.tag, _ = Tag.objects.get_or_create(name='Vegan', defaults={'slug': 'vegan'})

    def test_create_recipe(self):
        """Test creating a recipe"""
        recipe = Recipes.objects.create(
            author=self.user,
            title='Test Recipe',
            description='Test Description',
            instructions='Test Instructions',
            status='draft'
        )
        self.assertEqual(recipe.title, 'Test Recipe')
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.status, 'draft')

    def test_recipe_with_tags(self):
        """Test recipe with tags relationship"""
        recipe = Recipes.objects.create(
            author=self.user,
            title='Tagged Recipe',
            description='Test',
            status='published'
        )
        recipe.tags.add(self.tag)

        self.assertEqual(recipe.tags.count(), 1)
        self.assertEqual(recipe.tags.first().name, 'Vegan')

    def test_recipe_with_ingredients(self):
        """Test recipe with ingredients relationship"""
        recipe = Recipes.objects.create(
            author=self.user,
            title='Recipe with Ingredients',
            description='Test',
            status='published'
        )
        ingredient = Ingredients.objects.create(name='tomato')
        RecipeIngredients.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            quantity=Decimal('100'),
            unit='g'
        )

        self.assertEqual(recipe.recipe_ingredients.count(), 1)
        self.assertEqual(recipe.recipe_ingredients.first().ingredient.name, 'tomato')


class RecipeAPITests(TestCase):
    """Test Recipe API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )

    def test_list_recipes_unauthenticated(self):
        """Test that unauthenticated users cannot list recipes"""
        response = self.client.get('/recipes/recipes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_recipes_authenticated(self):
        """Test listing recipes when authenticated"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/recipes/recipes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check paginated response structure
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_create_recipe_unauthenticated(self):
        """Test that unauthenticated users cannot create recipes"""
        data = {
            'title': 'Test Recipe',
            'description': 'Test Description',
            'instructions': 'Test Instructions',
            'status': 'draft'
        }
        response = self.client.post('/recipes/recipes/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_recipe_authenticated(self):
        """Test creating a recipe when authenticated"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Test Recipe',
            'description': 'Test Description',
            'instructions': 'Test Instructions',
            'status': 'draft',
            'recipe_ingredients': []
        }
        response = self.client.post('/recipes/recipes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Recipe')
        self.assertEqual(response.data['author'], self.user.id)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Recipe with Ingredients',
            'description': 'Test',
            'instructions': 'Mix ingredients',
            'status': 'draft',
            'recipe_ingredients': [
                {
                    'ingredient': {'name': 'tomato'},
                    'quantity': '100',
                    'unit': 'g'
                },
                {
                    'ingredient': {'name': 'onion'},
                    'quantity': '50',
                    'unit': 'g'
                }
            ]
        }
        response = self.client.post('/recipes/recipes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['ingredients']), 2)

    def test_retrieve_recipe(self):
        """Test retrieving a single recipe"""
        self.client.force_authenticate(user=self.user)
        recipe = Recipes.objects.create(
            author=self.user,
            title='Test Recipe',
            description='Test',
            status='published'
        )
        response = self.client.get(f'/recipes/recipes/{recipe.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Recipe')

    def test_update_recipe(self):
        """Test updating a recipe"""
        self.client.force_authenticate(user=self.user)
        recipe = Recipes.objects.create(
            author=self.user,
            title='Original Title',
            description='Test',
            status='draft'
        )
        data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'instructions': 'Updated Instructions',
            'status': 'published'
        }
        response = self.client.patch(f'/recipes/recipes/{recipe.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.assertEqual(response.data['status'], 'published')

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        self.client.force_authenticate(user=self.user)
        recipe = Recipes.objects.create(
            author=self.user,
            title='To Delete',
            description='Test',
            status='draft'
        )
        response = self.client.delete(f'/recipes/recipes/{recipe.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipes.objects.filter(id=recipe.id).exists())


class RecipePermissionsTests(TestCase):
    """Test recipe permissions and authorization"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.recipe = Recipes.objects.create(
            author=self.user,
            title='Test Recipe',
            description='Test',
            status='published'
        )

    def test_owner_can_update_recipe(self):
        """Test that recipe owner can update their recipe"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated by Owner'}
        response = self.client.patch(f'/recipes/recipes/{self.recipe.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cannot_update_recipe(self):
        """Test that non-owner cannot update recipe"""
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Updated by Other'}
        response = self.client.patch(f'/recipes/recipes/{self.recipe.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_recipe(self):
        """Test that admin can update any recipe"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'title': 'Updated by Admin'}
        response = self.client.patch(f'/recipes/recipes/{self.recipe.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_delete_recipe(self):
        """Test that recipe owner can delete their recipe"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/recipes/recipes/{self.recipe.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_owner_cannot_delete_recipe(self):
        """Test that non-owner cannot delete recipe"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f'/recipes/recipes/{self.recipe.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_any_recipe(self):
        """Test that admin can delete any recipe"""
        recipe = Recipes.objects.create(
            author=self.other_user,
            title='Other Recipe',
            description='Test',
            status='published'
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/recipes/recipes/{recipe.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RecipeFilterTests(TestCase):
    """Test recipe filtering and search functionality"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.tag_vegan, _ = Tag.objects.get_or_create(name='Vegan', defaults={'slug': 'vegan'})
        self.tag_quick, _ = Tag.objects.get_or_create(name='Quick', defaults={'slug': 'quick'})

        # Create test recipes
        self.recipe1 = Recipes.objects.create(
            author=self.user,
            title='Vegan Pasta',
            description='Quick vegan pasta recipe',
            status='published'
        )
        self.recipe1.tags.add(self.tag_vegan, self.tag_quick)

        self.recipe2 = Recipes.objects.create(
            author=self.user,
            title='Vegan Soup',
            description='Healthy soup',
            status='published'
        )
        self.recipe2.tags.add(self.tag_vegan)

        self.recipe3 = Recipes.objects.create(
            author=self.user,
            title='Chicken Stir Fry',
            description='Quick chicken dish',
            status='published'
        )
        self.recipe3.tags.add(self.tag_quick)

        self.client.force_authenticate(user=self.user)

    def test_search_by_title(self):
        """Test searching recipes by title"""
        response = self.client.get('/recipes/recipes/search/?q=Vegan')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Vegan Pasta and Vegan Soup

    def test_search_by_description(self):
        """Test searching recipes by description"""
        response = self.client.get('/recipes/recipes/search/?q=Quick')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Vegan Pasta and Chicken Stir Fry

    def test_search_empty_query(self):
        """Test search with empty query returns empty list"""
        response = self.client.get('/recipes/recipes/search/?q=')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_search_query_too_long(self):
        """Test search with query longer than 200 characters fails"""
        long_query = 'a' * 201
        response = self.client.get(f'/recipes/recipes/search/?q={long_query}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('too long', response.data['error'].lower())

    def test_filter_by_single_tag_any_mode(self):
        """Test filtering by single tag (OR mode)"""
        response = self.client.get(f'/recipes/recipes/filter_by_tags/?tag_ids={self.tag_vegan.id}&match=any')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Vegan Pasta and Vegan Soup

    def test_filter_by_multiple_tags_any_mode(self):
        """Test filtering by multiple tags (OR mode)"""
        response = self.client.get(f'/recipes/recipes/filter_by_tags/?tag_ids={self.tag_vegan.id},{self.tag_quick.id}&match=any')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # All recipes have at least one tag

    def test_filter_by_multiple_tags_all_mode(self):
        """Test filtering by multiple tags (AND mode)"""
        response = self.client.get(f'/recipes/recipes/filter_by_tags/?tag_ids={self.tag_vegan.id},{self.tag_quick.id}&match=all')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only Vegan Pasta has both tags

    def test_filter_by_tags_too_many_tags(self):
        """Test filtering with more than 20 tags fails"""
        tag_ids = ','.join([str(i) for i in range(1, 22)])
        response = self.client.get(f'/recipes/recipes/filter_by_tags/?tag_ids={tag_ids}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('too many', response.data['error'].lower())

    def test_filter_by_tags_invalid_format(self):
        """Test filtering with invalid tag ID format fails"""
        response = self.client.get('/recipes/recipes/filter_by_tags/?tag_ids=abc,def')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_my_recipes(self):
        """Test getting only current user's recipes"""
        other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123'
        )
        Recipes.objects.create(
            author=other_user,
            title='Other User Recipe',
            description='Test',
            status='published'
        )

        response = self.client.get('/recipes/recipes/my_recipes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Only current user's 3 recipes


class RecipeLikeSaveTests(TestCase):
    """Test recipe like and save functionality"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.recipe = Recipes.objects.create(
            author=self.user,
            title='Test Recipe',
            description='Test',
            status='published'
        )
        self.client.force_authenticate(user=self.user)

    def test_toggle_like_add(self):
        """Test liking a recipe"""
        response = self.client.post(f'/recipes/recipes/{self.recipe.id}/toggle_like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 1)
        self.assertTrue(RecipeLikes.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_toggle_like_remove(self):
        """Test unliking a recipe"""
        RecipeLikes.objects.create(user=self.user, recipe=self.recipe)

        response = self.client.post(f'/recipes/recipes/{self.recipe.id}/toggle_like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 0)
        self.assertFalse(RecipeLikes.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_toggle_save_add(self):
        """Test saving a recipe"""
        response = self.client.post(f'/recipes/recipes/{self.recipe.id}/toggle_save/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['saved'])
        self.assertTrue(Favorites.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_toggle_save_remove(self):
        """Test unsaving a recipe"""
        Favorites.objects.create(user=self.user, recipe=self.recipe)

        response = self.client.post(f'/recipes/recipes/{self.recipe.id}/toggle_save/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['saved'])
        self.assertFalse(Favorites.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_get_saved_recipes(self):
        """Test retrieving saved recipes"""
        recipe2 = Recipes.objects.create(
            author=self.user,
            title='Recipe 2',
            description='Test',
            status='published'
        )
        Favorites.objects.create(user=self.user, recipe=self.recipe)
        Favorites.objects.create(user=self.user, recipe=recipe2)

        response = self.client.get('/recipes/recipes/saved/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_recipe_serializer_includes_like_save_status(self):
        """Test that recipe serializer includes is_liked and is_saved fields"""
        RecipeLikes.objects.create(user=self.user, recipe=self.recipe)
        Favorites.objects.create(user=self.user, recipe=self.recipe)

        response = self.client.get(f'/recipes/recipes/{self.recipe.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_liked'])
        self.assertTrue(response.data['is_saved'])
        self.assertEqual(response.data['likes_count'], 1)


class TagAPITests(TestCase):
    """Test Tag API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        Tag.objects.get_or_create(name='Vegan', defaults={'slug': 'vegan', 'is_active': True})
        Tag.objects.get_or_create(name='Gluten-free', defaults={'slug': 'gluten-free', 'is_active': True})
        Tag.objects.get_or_create(name='Inactive', defaults={'slug': 'inactive', 'is_active': False})

    def test_list_tags_unauthenticated(self):
        """Test that unauthenticated users cannot list tags"""
        response = self.client.get('/recipes/tags/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_tags_authenticated(self):
        """Test listing tags when authenticated"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/recipes/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check paginated response structure
        self.assertIn('results', response.data)
        # Check that we get at least the 2 active tags we created
        self.assertGreaterEqual(len(response.data['results']), 2)
        # Verify specific tags are present
        tag_names = [tag['name'] for tag in response.data['results']]
        self.assertIn('Vegan', tag_names)
        self.assertIn('Gluten-free', tag_names)

    def test_list_tags_excludes_inactive(self):
        """Test that inactive tags are not listed"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/recipes/tags/')
        # Access results from paginated response
        tag_names = [tag['name'] for tag in response.data['results']]
        self.assertNotIn('Inactive', tag_names)

    def test_retrieve_tag(self):
        """Test retrieving a single tag"""
        self.client.force_authenticate(user=self.user)
        tag = Tag.objects.get(slug='vegan')
        response = self.client.get(f'/recipes/tags/{tag.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Vegan')
