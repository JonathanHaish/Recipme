from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Goal, DietType


class GoalSerializer(serializers.ModelSerializer):
    """Serializer for Goal model"""
    class Meta:
        model = Goal
        fields = ['id', 'code', 'name', 'description', 'is_active', 'display_order']


class DietTypeSerializer(serializers.ModelSerializer):
    """Serializer for DietType model"""
    class Meta:
        model = DietType
        fields = ['id', 'code', 'name', 'description', 'is_active', 'display_order']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    Includes username from related User model.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    profile_image_url = serializers.SerializerMethodField()
    goals = GoalSerializer(many=True, read_only=True)
    diet = DietTypeSerializer(read_only=True)
    # For writing - accept goal IDs and diet ID
    goal_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Goal.objects.filter(is_active=True),
        write_only=True,
        required=False,
        source='goals'
    )
    diet_id = serializers.PrimaryKeyRelatedField(
        queryset=DietType.objects.filter(is_active=True),
        write_only=True,
        required=False,
        source='diet',
        allow_null=True
    )

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'profile_image',
            'profile_image_url',
            'goals',
            'goal_ids',
            'diet',
            'diet_id',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_profile_image_url(self, obj):
        """Return the full URL of the profile image if it exists"""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    Allows partial updates.
    """
    profile_image_url = serializers.SerializerMethodField()
    # For writing - accept goal IDs and diet ID
    goal_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Goal.objects.filter(is_active=True),
        write_only=True,
        required=False,
        source='goals'
    )
    diet_id = serializers.PrimaryKeyRelatedField(
        queryset=DietType.objects.filter(is_active=True),
        write_only=True,
        required=False,
        source='diet',
        allow_null=True
    )

    class Meta:
        model = UserProfile
        fields = [
            'profile_image',
            'profile_image_url',
            'goal_ids',
            'diet_id',
            'description',
        ]

    def get_profile_image_url(self, obj):
        """Return the full URL of the profile image if it exists"""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None
