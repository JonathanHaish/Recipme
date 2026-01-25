# Generated manually for recipe tagging system
# Data migration to create predefined tags

from django.db import migrations
from django.utils.text import slugify


def create_default_tags(apps, schema_editor):
    """Create 6 predefined recipe tags"""
    Tag = apps.get_model('recipes', 'Tag')

    default_tags = [
        {
            'name': 'Vegan',
            'slug': 'vegan',
            'description': 'Contains no animal products',
        },
        {
            'name': 'Vegetarian',
            'slug': 'vegetarian',
            'description': 'Does not contain meat or fish',
        },
        {
            'name': 'Lactose-free',
            'slug': 'lactose-free',
            'description': 'Contains no dairy products',
        },
        {
            'name': 'Flour-free',
            'slug': 'flour-free',
            'description': 'Does not contain wheat or grain flour',
        },
        {
            'name': 'Full of protein',
            'slug': 'full-of-protein',
            'description': 'High protein content',
        },
        {
            'name': 'Full of vegetables',
            'slug': 'full-of-vegetables',
            'description': 'Rich in vegetables',
        },
    ]

    for tag_data in default_tags:
        Tag.objects.get_or_create(
            slug=tag_data['slug'],
            defaults={
                'name': tag_data['name'],
                'description': tag_data['description'],
                'is_active': True,
            }
        )


def reverse_migration(apps, schema_editor):
    """Remove the predefined tags"""
    Tag = apps.get_model('recipes', 'Tag')
    slugs = ['vegan', 'vegetarian', 'lactose-free', 'flour-free', 'full-of-protein', 'full-of-vegetables']
    Tag.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_recipes_tags'),
    ]

    operations = [
        migrations.RunPython(create_default_tags, reverse_migration),
    ]
