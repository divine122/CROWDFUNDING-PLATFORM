from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from rest_framework import response,status,permissions,views
from drf_yasg import openapi
from campaign.models import Campaign
from . models import Comment
from . serializers import CommentSerializer
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema



class CreateCommentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def post(self, request, campaign_id, *args, **kwargs):
        campaign = Campaign.objects.filter(id=campaign_id).first()  # Assuming Project model exists
        if not Campaign:
            raise NotFound("Campaign not found")

        # Create a comment object and associate it with the project and the user
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(user=request.user, campaign=campaign)  # Save the comment
            return response.Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class CommentListView(views.APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  
    serializer_class = CommentSerializer

    
    @swagger_auto_schema(operation_description="Retrieve a list of comments")
    def get(self, request, *args, **kwargs):
        # Fetch the comments from the database
        comments = Comment.objects.all()  # Replace with your query
        serializer = CommentSerializer(comments, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    



class CommentModerationView(views.APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admins can moderate comments

    @swagger_auto_schema(
        operation_description="Approve or reject a comment.",
        request_body=CommentSerializer,  # Use CommentSerializer to show the structure of request body
        responses={
            200: CommentSerializer,  # Return the updated comment in the response
            400: 'Bad Request, `is_approved` is required',  # Show a simple description for 400 error
            404: 'Comment not found',  # Show a simple description for 404 error
        }
    )
    def patch(self, request, comment_id, *args, **kwargs):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise NotFound("Comment not found")

        # Get the `is_approved` flag from the request data
        is_approved = request.data.get("is_approved", None)
        
        if is_approved is not None:
            # Update the `is_approved` field and save the comment
            comment.is_approved = is_approved
            comment.save()
            return response.Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)
        
        # If `is_approved` is missing in the request data, return an error
        return response.Response({"detail": "is_approved is required"}, status=status.HTTP_400_BAD_REQUEST)


class CommentDeleteView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return response.Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        comment.status = 'deleted'
        comment.save()

        return response.Response({"detail": "Comment deleted"}, status=status.HTTP_200_OK)

    
