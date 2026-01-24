# Generated manually - Populate initial Goals and DietTypes

from django.db import migrations


def populate_goals_and_diettypes(apps, schema_editor):
    """Populate initial Goals and DietTypes"""
    Goal = apps.get_model('profiles', 'Goal')
    DietType = apps.get_model('profiles', 'DietType')
    
    # Create Goals - Comprehensive list for recipe/nutrition app
    goals_data = [
        {'code': 'weight_loss', 'name': 'Weight Loss', 'description': 'Lose weight and maintain a healthy body weight', 'display_order': 1},
        {'code': 'weight_gain', 'name': 'Weight Gain', 'description': 'Gain weight in a healthy way', 'display_order': 2},
        {'code': 'muscle_gain', 'name': 'Muscle Gain', 'description': 'Build muscle mass and strength', 'display_order': 3},
        {'code': 'maintain_weight', 'name': 'Maintain Weight', 'description': 'Maintain current weight', 'display_order': 4},
        {'code': 'improve_health', 'name': 'Improve Health', 'description': 'Improve overall health and wellbeing', 'display_order': 5},
        {'code': 'increase_energy', 'name': 'Increase Energy', 'description': 'Boost energy levels throughout the day', 'display_order': 6},
        {'code': 'better_nutrition', 'name': 'Better Nutrition', 'description': 'Improve nutritional intake and eating habits', 'display_order': 7},
        {'code': 'meal_prep', 'name': 'Meal Prep', 'description': 'Plan and prepare meals in advance', 'display_order': 8},
        {'code': 'healthy_eating', 'name': 'Healthy Eating', 'description': 'Adopt healthier eating patterns', 'display_order': 9},
        {'code': 'build_strength', 'name': 'Build Strength', 'description': 'Increase physical strength and endurance', 'display_order': 10},
        {'code': 'improve_digestion', 'name': 'Improve Digestion', 'description': 'Support digestive health', 'display_order': 11},
        {'code': 'heart_health', 'name': 'Heart Health', 'description': 'Support cardiovascular health', 'display_order': 12},
        {'code': 'diabetes_management', 'name': 'Diabetes Management', 'description': 'Manage blood sugar levels', 'display_order': 13},
        {'code': 'reduce_inflammation', 'name': 'Reduce Inflammation', 'description': 'Follow anti-inflammatory diet', 'display_order': 14},
        {'code': 'boost_immunity', 'name': 'Boost Immunity', 'description': 'Strengthen immune system through nutrition', 'display_order': 15},
        {'code': 'improve_skin', 'name': 'Improve Skin Health', 'description': 'Support healthy skin through diet', 'display_order': 16},
        {'code': 'better_sleep', 'name': 'Better Sleep', 'description': 'Improve sleep quality through nutrition', 'display_order': 17},
        {'code': 'sports_performance', 'name': 'Sports Performance', 'description': 'Optimize nutrition for athletic performance', 'display_order': 18},
    ]
    
    for goal_data in goals_data:
        Goal.objects.get_or_create(
            code=goal_data['code'],
            defaults={
                'name': goal_data['name'],
                'description': goal_data['description'],
                'display_order': goal_data['display_order'],
                'is_active': True,
            }
        )
    
    # Create DietTypes - Comprehensive list for recipe/nutrition app
    diet_types_data = [
        {'code': 'none', 'name': 'No Specific Diet', 'description': 'No specific dietary restrictions or preferences', 'display_order': 0},
        {'code': 'vegan', 'name': 'Vegan', 'description': 'Plant-based diet excluding all animal products', 'display_order': 1},
        {'code': 'vegetarian', 'name': 'Vegetarian', 'description': 'Diet excluding meat and fish', 'display_order': 2},
        {'code': 'pescatarian', 'name': 'Pescatarian', 'description': 'Vegetarian diet that includes fish and seafood', 'display_order': 3},
        {'code': 'keto', 'name': 'Keto', 'description': 'Low-carb, high-fat ketogenic diet', 'display_order': 4},
        {'code': 'paleo', 'name': 'Paleo', 'description': 'Paleolithic diet focusing on whole foods', 'display_order': 5},
        {'code': 'mediterranean', 'name': 'Mediterranean', 'description': 'Mediterranean-style diet rich in fruits, vegetables, and healthy fats', 'display_order': 6},
        {'code': 'gluten_free', 'name': 'Gluten-Free', 'description': 'Diet excluding gluten-containing foods', 'display_order': 7},
        {'code': 'lactose_free', 'name': 'Lactose-Free', 'description': 'Diet excluding lactose-containing dairy products', 'display_order': 8},
        {'code': 'dairy_free', 'name': 'Dairy-Free', 'description': 'Diet excluding all dairy products', 'display_order': 9},
        {'code': 'low_carb', 'name': 'Low Carb', 'description': 'Low carbohydrate diet', 'display_order': 10},
        {'code': 'low_fat', 'name': 'Low Fat', 'description': 'Low fat diet', 'display_order': 11},
        {'code': 'low_sodium', 'name': 'Low Sodium', 'description': 'Diet with reduced sodium intake', 'display_order': 12},
        {'code': 'high_protein', 'name': 'High Protein', 'description': 'Diet focused on high protein intake', 'display_order': 13},
        {'code': 'whole30', 'name': 'Whole30', 'description': '30-day elimination diet focusing on whole foods', 'display_order': 14},
        {'code': 'dash', 'name': 'DASH Diet', 'description': 'Dietary Approaches to Stop Hypertension', 'display_order': 15},
        {'code': 'fodmap', 'name': 'Low FODMAP', 'description': 'Diet low in fermentable oligosaccharides, disaccharides, monosaccharides and polyols', 'display_order': 16},
        {'code': 'raw_food', 'name': 'Raw Food', 'description': 'Diet consisting mainly of uncooked, unprocessed foods', 'display_order': 17},
        {'code': 'intermittent_fasting', 'name': 'Intermittent Fasting', 'description': 'Eating pattern that cycles between periods of eating and fasting', 'display_order': 18},
        {'code': 'flexitarian', 'name': 'Flexitarian', 'description': 'Primarily vegetarian diet with occasional meat consumption', 'display_order': 19},
        {'code': 'nut_free', 'name': 'Nut-Free', 'description': 'Diet excluding all tree nuts and peanuts', 'display_order': 20},
        {'code': 'egg_free', 'name': 'Egg-Free', 'description': 'Diet excluding eggs', 'display_order': 21},
        {'code': 'soy_free', 'name': 'Soy-Free', 'description': 'Diet excluding soy products', 'display_order': 22},
        {'code': 'halal', 'name': 'Halal', 'description': 'Diet following Islamic dietary laws', 'display_order': 23},
        {'code': 'kosher', 'name': 'Kosher', 'description': 'Diet following Jewish dietary laws', 'display_order': 24},
    ]
    
    for diet_data in diet_types_data:
        DietType.objects.get_or_create(
            code=diet_data['code'],
            defaults={
                'name': diet_data['name'],
                'description': diet_data['description'],
                'display_order': diet_data['display_order'],
                'is_active': True,
            }
        )


def reverse_populate(apps, schema_editor):
    """Reverse migration - remove all goals and diet types"""
    Goal = apps.get_model('profiles', 'Goal')
    DietType = apps.get_model('profiles', 'DietType')
    
    Goal.objects.all().delete()
    DietType.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_goals_diettypes'),
    ]

    operations = [
        migrations.RunPython(populate_goals_and_diettypes, reverse_populate),
    ]
