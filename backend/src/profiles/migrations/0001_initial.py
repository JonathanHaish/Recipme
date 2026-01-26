# Generated manually for profiles app

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
            name='DietType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text="Internal code (e.g., 'vegan')", max_length=50, unique=True)),
                ('name', models.CharField(help_text="Display name (e.g., 'Vegan')", max_length=100)),
                ('description', models.TextField(blank=True, help_text='Optional description')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this diet type is available for selection')),
                ('display_order', models.IntegerField(default=0, help_text='Order for display in forms')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Diet Type',
                'verbose_name_plural': 'Diet Types',
                'db_table': 'diet_types',
                'ordering': ['display_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text="Internal code (e.g., 'weight_loss')", max_length=50, unique=True)),
                ('name', models.CharField(help_text="Display name (e.g., 'Weight Loss')", max_length=100)),
                ('description', models.TextField(blank=True, help_text='Optional description')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this goal is available for selection')),
                ('display_order', models.IntegerField(default=0, help_text='Order for display in forms')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Goal',
                'verbose_name_plural': 'Goals',
                'db_table': 'goals',
                'ordering': ['display_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('profile_image', models.ImageField(blank=True, help_text='User profile picture', null=True, upload_to='profile_images/')),
                ('description', models.TextField(blank=True, default='', help_text="User's description of their goals and preferences")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('diet', models.ForeignKey(blank=True, help_text="User's dietary preference", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_profiles', to='profiles.diettype')),
                ('goals', models.ManyToManyField(blank=True, help_text="User's selected goals", related_name='user_profiles', to='profiles.goal')),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'User Profiles',
                'db_table': 'user_profiles',
            },
        ),
    ]
