# Generated manually for Recipes image field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_recipeingredients_fdc_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipes',
            name='image',
            field=models.ImageField(blank=True, help_text='Recipe image', null=True, upload_to='recipe_images/'),
        ),
    ]
