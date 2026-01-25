# Generated manually for nutrition fields cleanup

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_create_default_tags'),
    ]

    operations = [
        # Remove sodium_mg field
        migrations.RemoveField(
            model_name='recipenutrition',
            name='sodium_mg',
        ),
        # Add fat_g field
        migrations.AddField(
            model_name='recipenutrition',
            name='fat_g',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
        # Add sugars_g field
        migrations.AddField(
            model_name='recipenutrition',
            name='sugars_g',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
    ]
