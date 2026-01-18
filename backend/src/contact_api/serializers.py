from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for creating contact messages.
    User is set automatically from the request context.
    """
    
    class Meta:
        model = ContactMessage
        fields = ['id', 'subject', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_subject(self, value):
        """Ensure subject is not empty or just whitespace"""
        if not value.strip():
            raise serializers.ValidationError("Subject cannot be empty.")
        return value.strip()

    def validate_message(self, value):
        """Ensure message is not empty or just whitespace"""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()

    def create(self, validated_data):
        """Create a new contact message with the authenticated user"""
        user = self.context['request'].user
        return ContactMessage.objects.create(user=user, **validated_data)
