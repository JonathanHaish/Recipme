# Data migration to populate default goals and diet types

from django.db import migrations


def populate_goals(apps, schema_editor):
    """Populate default goals"""
    Goal = apps.get_model('profiles', 'Goal')

    goals_data = [
        {'code': 'weight_loss', 'name': 'Weight Loss', 'description': 'Lose weight through healthy eating', 'display_order': 1},
        {'code': 'weight_gain', 'name': 'Weight Gain', 'description': 'Gain weight in a healthy way', 'display_order': 2},
        {'code': 'muscle_gain', 'name': 'Muscle Gain', 'description': 'Build muscle mass', 'display_order': 3},
        {'code': 'maintain_weight', 'name': 'Maintain Weight', 'description': 'Keep current weight', 'display_order': 4},
        {'code': 'improve_health', 'name': 'Improve Health', 'description': 'General health improvement', 'display_order': 5},
        {'code': 'increase_energy', 'name': 'Increase Energy', 'description': 'Boost energy levels', 'display_order': 6},
        {'code': 'better_nutrition', 'name': 'Better Nutrition', 'description': 'Improve overall nutrition', 'display_order': 7},
        {'code': 'meal_prep', 'name': 'Meal Prep', 'description': 'Plan and prepare meals ahead', 'display_order': 8},
        {'code': 'healthy_eating', 'name': 'Healthy Eating', 'description': 'Eat more wholesome foods', 'display_order': 9},
        {'code': 'build_strength', 'name': 'Build Strength', 'description': 'Increase physical strength', 'display_order': 10},
        {'code': 'improve_digestion', 'name': 'Improve Digestion', 'description': 'Better digestive health', 'display_order': 11},
        {'code': 'heart_health', 'name': 'Heart Health', 'description': 'Support cardiovascular health', 'display_order': 12},
        {'code': 'diabetes_management', 'name': 'Diabetes Management', 'description': 'Manage blood sugar levels', 'display_order': 13},
        {'code': 'reduce_inflammation', 'name': 'Reduce Inflammation', 'description': 'Anti-inflammatory eating', 'display_order': 14},
        {'code': 'boost_immunity', 'name': 'Boost Immunity', 'description': 'Strengthen immune system', 'display_order': 15},
        {'code': 'improve_skin', 'name': 'Improve Skin', 'description': 'Better skin health', 'display_order': 16},
        {'code': 'better_sleep', 'name': 'Better Sleep', 'description': 'Improve sleep quality', 'display_order': 17},
        {'code': 'sports_performance', 'name': 'Sports Performance', 'description': 'Enhance athletic performance', 'display_order': 18},
    ]

    for goal_data in goals_data:
        Goal.objects.get_or_create(
            code=goal_data['code'],
            defaults={
                'name': goal_data['name'],
                'description': goal_data['description'],
                'display_order': goal_data['display_order'],
                'is_active': True
            }
        )


def populate_diet_types(apps, schema_editor):
    """Populate default diet types"""
    DietType = apps.get_model('profiles', 'DietType')

    diet_types_data = [
        {'code': 'vegan', 'name': 'Vegan', 'description': 'Plant-based, no animal products', 'display_order': 1},
        {'code': 'vegetarian', 'name': 'Vegetarian', 'description': 'No meat or fish', 'display_order': 2},
        {'code': 'pescatarian', 'name': 'Pescatarian', 'description': 'Vegetarian plus fish/seafood', 'display_order': 3},
        {'code': 'keto', 'name': 'Keto', 'description': 'Very low carb, high fat', 'display_order': 4},
        {'code': 'paleo', 'name': 'Paleo', 'description': 'Whole foods, no grains or dairy', 'display_order': 5},
        {'code': 'gluten_free', 'name': 'Gluten-Free', 'description': 'No wheat, barley, or rye', 'display_order': 6},
        {'code': 'dairy_free', 'name': 'Dairy-Free', 'description': 'No milk or dairy products', 'display_order': 7},
        {'code': 'low_carb', 'name': 'Low-Carb', 'description': 'Reduced carbohydrate intake', 'display_order': 8},
        {'code': 'low_fat', 'name': 'Low-Fat', 'description': 'Reduced fat intake', 'display_order': 9},
        {'code': 'mediterranean', 'name': 'Mediterranean', 'description': 'Fish, olive oil, vegetables', 'display_order': 10},
        {'code': 'whole30', 'name': 'Whole30', 'description': 'Whole foods, no processed items', 'display_order': 11},
        {'code': 'lactose_free', 'name': 'Lactose-Free', 'description': 'No lactose-containing foods', 'display_order': 12},
        {'code': 'halal', 'name': 'Halal', 'description': 'Islamic dietary laws', 'display_order': 13},
        {'code': 'kosher', 'name': 'Kosher', 'description': 'Jewish dietary laws', 'display_order': 14},
    ]

    for diet_data in diet_types_data:
        DietType.objects.get_or_create(
            code=diet_data['code'],
            defaults={
                'name': diet_data['name'],
                'description': diet_data['description'],
                'display_order': diet_data['display_order'],
                'is_active': True
            }
        )


def reverse_populate(apps, schema_editor):
    """Remove all goals and diet types"""
    Goal = apps.get_model('profiles', 'Goal')
    DietType = apps.get_model('profiles', 'DietType')

    Goal.objects.all().delete()
    DietType.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_goals, reverse_populate),
        migrations.RunPython(populate_diet_types, reverse_populate),
    ]
