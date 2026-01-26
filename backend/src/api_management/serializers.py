from rest_framework import serializers

class FoodTaglineSerializer(serializers.Serializer):
    """Serializer for the object returned from generate_product_tagline"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.CharField()
    description = serializers.CharField()  # Holds the brand/company name according to your logic
    fat_str = serializers.CharField()

class IngredientSearchResponseSerializer(serializers.Serializer):
    """Serializer for the API response wrapper (success/error)"""
    success = serializers.BooleanField()
    res = FoodTaglineSerializer(many=True, required=False)  # Changed from 'data' to 'res' to match frontend expectations
    error = serializers.CharField(required=False, allow_null=True)
    status = serializers.IntegerField(required=False)
