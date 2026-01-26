from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile, Goal, DietType
from .serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    GoalSerializer,
    DietTypeSerializer
)
import logging

logger = logging.getLogger(__name__)


class GoalListView(APIView):
    """
    View to get all active goals.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        goals = Goal.objects.filter(is_active=True)
        serializer = GoalSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DietTypeListView(APIView):
    """
    View to get all active diet types.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        diet_types = DietType.objects.filter(is_active=True)
        serializer = DietTypeSerializer(diet_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    View to get and update the current user's profile.
    Only authenticated users can access their own profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get the current user's profile.
        Creates a profile if it doesn't exist.
        """
        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update the current user's profile.
        Allows partial updates.
        Handles both JSON and FormData (for file uploads).
        """
        logger.info(f"=== Profile Update Request ===")
        logger.info(f"User: {request.user.username}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Raw data type: {type(request.data)}")
        logger.info(f"Raw data keys: {request.data.keys() if hasattr(request.data, 'keys') else 'N/A'}")

        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )

        # Handle FormData - QueryDict returns lists for each key
        # Convert QueryDict to regular dict, extracting first element from lists
        data = {}
        for key, value in request.data.items():
            # For FormData, QueryDict returns lists, so get the first element
            if isinstance(value, list):
                if len(value) > 0:
                    # Check if the first element is itself a list (nested)
                    if isinstance(value[0], list):
                        # If nested list, use it directly (shouldn't happen, but handle it)
                        data[key] = value[0]
                    else:
                        # Normal case: list with string/values
                        data[key] = value[0]
                else:
                    # Empty list
                    data[key] = None
            else:
                data[key] = value

        # Handle goal_ids - parse JSON string if it's a string, or handle as list
        if 'goal_ids' in data and data['goal_ids'] is not None:
            goal_ids_value = data['goal_ids']
            if isinstance(goal_ids_value, str):
                try:
                    import json
                    # Remove any whitespace and parse
                    goal_ids_value = goal_ids_value.strip()
                    if goal_ids_value:
                        parsed = json.loads(goal_ids_value)
                        if isinstance(parsed, list):
                            data['goal_ids'] = parsed
                        else:
                            data['goal_ids'] = []
                    else:
                        data['goal_ids'] = []
                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    logger.warning(f"Failed to parse goal_ids JSON: {e}, value: {goal_ids_value}")
                    data['goal_ids'] = []
            elif isinstance(goal_ids_value, list):
                # Already a list
                data['goal_ids'] = goal_ids_value
            else:
                data['goal_ids'] = []
        elif 'goal_ids' not in data:
            # If goal_ids not provided, don't include it (partial update)
            data.pop('goal_ids', None)

        # Handle diet_id - convert string to int or None
        if 'diet_id' in data and data['diet_id'] is not None:
            diet_id_value = data['diet_id']
            if isinstance(diet_id_value, str):
                # Empty string or 'none' means no diet
                if diet_id_value.strip() == '' or diet_id_value.strip() == 'none':
                    data['diet_id'] = None
                else:
                    try:
                        data['diet_id'] = int(diet_id_value)
                    except (ValueError, TypeError):
                        data['diet_id'] = None
            elif isinstance(diet_id_value, int):
                data['diet_id'] = diet_id_value
            else:
                data['diet_id'] = None
        elif 'diet_id' not in data:
            # If diet_id not provided, don't include it (partial update)
            data.pop('diet_id', None)

        logger.info(f"Processed data for serializer: {data}")

        serializer = UserProfileUpdateSerializer(
            profile,
            data=data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            # Return full profile data
            full_serializer = UserProfileSerializer(profile, context={'request': request})
            logger.info(f"Profile updated successfully")
            return Response(full_serializer.data, status=status.HTTP_200_OK)

        # Return detailed error information
        logger.error(f"Profile update validation errors: {serializer.errors}")
        logger.error(f"Processed data: {data}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Alias for PUT to allow partial updates"""
        return self.put(request)
