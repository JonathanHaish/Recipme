from django.db import models
from django.contrib.auth.models import User


class Goal(models.Model):
    """
    Model for user goals that can be managed by admin.
    """
    code = models.CharField(max_length=50, unique=True, help_text="Internal code (e.g., 'weight_loss')")
    name = models.CharField(max_length=100, help_text="Display name (e.g., 'Weight Loss')")
    description = models.TextField(blank=True, help_text="Optional description")
    is_active = models.BooleanField(default=True, help_text="Whether this goal is available for selection")
    display_order = models.IntegerField(default=0, help_text="Order for display in forms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'goals'
        verbose_name = "Goal"
        verbose_name_plural = "Goals"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class DietType(models.Model):
    """
    Model for diet types that can be managed by admin.
    """
    code = models.CharField(max_length=50, unique=True, help_text="Internal code (e.g., 'vegan')")
    name = models.CharField(max_length=100, help_text="Display name (e.g., 'Vegan')")
    description = models.TextField(blank=True, help_text="Optional description")
    is_active = models.BooleanField(default=True, help_text="Whether this diet type is available for selection")
    display_order = models.IntegerField(default=0, help_text="Order for display in forms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'diet_types'
        verbose_name = "Diet Type"
        verbose_name_plural = "Diet Types"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    User profile model connected to Django User model by username.
    Stores user goals, diet preferences, profile image, and description.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    
    # Profile image
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        help_text="User profile picture"
    )
    
    # Goals - ManyToMany relationship with Goal model
    goals = models.ManyToManyField(
        Goal,
        related_name='user_profiles',
        blank=True,
        help_text="User's selected goals"
    )
    
    # Diet preference - ForeignKey to DietType model
    diet = models.ForeignKey(
        DietType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        help_text="User's dietary preference"
    )
    
    # Description of goals and more
    description = models.TextField(
        blank=True,
        default='',
        help_text="User's description of their goals and preferences"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"Profile for {self.user.username}"
