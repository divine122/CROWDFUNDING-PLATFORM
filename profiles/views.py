from django.shortcuts import render

# Create your views here.

from rest_framework import status, permissions, views, generics, parsers, response

from .models import UserProfile

from .serializers import UserProfileSerializer
from rest_framework import status, permissions, views, response
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access

    def get(self, request, *args, **kwargs):
        # Get the authenticated user
        user = request.user
        serializer = UserProfileSerializer(user)
        return response.Response(serializer.data)

    def put(self, request, *args, **kwargs):
        # Update the authenticated user's profile
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)