from rest_framework import serializers

class FoodTaglineSerializer(serializers.Serializer):
    """סריליאזר עבור האובייקט שמוחזר מ-generate_product_tagline"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.CharField()
    description = serializers.CharField()  # זה מחזיק את שם המותג/החברה לפי הלוגיקה שלך
    fat_str = serializers.CharField()

class IngredientSearchResponseSerializer(serializers.Serializer):
    """סריליאזר עבור מעטפת התגובה מה-API (הצלחה/שגיאה)"""
    success = serializers.BooleanField()
    res = FoodTaglineSerializer(many=True, required=False)  # Changed from 'data' to 'res' to match frontend expectations
    error = serializers.CharField(required=False, allow_null=True)
    status = serializers.IntegerField(required=False)
