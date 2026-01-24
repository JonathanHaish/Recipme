# Generated manually for UserProfile model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('profile_image', models.ImageField(blank=True, help_text='User profile picture', null=True, upload_to='profile_images/')),
                ('goals', models.JSONField(default=list, help_text="List of user goals (e.g., ['weight_loss', 'muscle_gain'])")),
                ('diet', models.CharField(choices=[('none', 'No Specific Diet'), ('vegan', 'Vegan'), ('vegetarian', 'Vegetarian'), ('pescatarian', 'Pescatarian'), ('keto', 'Keto'), ('paleo', 'Paleo'), ('mediterranean', 'Mediterranean'), ('gluten_free', 'Gluten-Free'), ('lactose_free', 'Lactose-Free'), ('low_carb', 'Low Carb'), ('low_fat', 'Low Fat')], default='none', help_text="User's dietary preference", max_length=50)),
                ('description', models.TextField(blank=True, default='', help_text="User's description of their goals and preferences")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'User Profiles',
                'db_table': 'user_profiles',
            },
        ),
    ]
