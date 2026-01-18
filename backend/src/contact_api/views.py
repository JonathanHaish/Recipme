from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ContactMessageSerializer


class ContactMessageCreateView(APIView):
    """
    API endpoint to create a new contact message.
    Requires authentication - message is associated with the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a new contact message from an authenticated user.
        
        Request body:
        - subject: string (required)
        - message: string (required)
        
        Returns 201 Created with message details on success.
        """
        serializer = ContactMessageSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Your message has been sent successfully. We will get back to you soon.',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
