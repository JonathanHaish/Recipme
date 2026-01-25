# Generated manually for recipe tagging system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_tag_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipes',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='recipes', to='recipes.tag'),
        ),
    ]
