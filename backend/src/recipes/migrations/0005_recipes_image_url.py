# Generated manually - Change image field to image_url URLField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_recipes_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipes',
            name='image',
        ),
        migrations.AddField(
            model_name='recipes',
            name='image_url',
            field=models.URLField(blank=True, help_text='URL to recipe image stored in frontend container', max_length=500, null=True),
        ),
    ]
