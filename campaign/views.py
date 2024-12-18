from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from .models import Campaign,CampaignPage
from rest_framework import status,permissions,response,views
from.serializers import CampaignSerializer,CreateCampaignSerializer,CampaignPageSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser,FormParser
from django.db.models import Count
from rest_framework.schemas import AutoSchema
from django.db.models.functions import TruncDate
from .engines import recommend_campaigns

class CampaignView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CampaignSerializer
    parser_classes = (MultiPartParser, FormParser)


    @swagger_auto_schema(request_body=CampaignSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Assign the current user to the created_by field
            campaign = serializer.save(created_by=request.user)
            return response.Response({"message": "Campaign created successfully", "project": campaign.id}, status=201)
        return response.Response(serializer.errors, status=400)

   

class CreateCampaignView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateCampaignSerializer 
   

    @swagger_auto_schema(request_body=CampaignSerializer)
    def post(self,request):
        user = request.user
        data = request.data
        if Campaign.objects.filter(created_by=user , status= 'active').exists():
            return response.Response(
                {'error':'you alraedy have an active campaign'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CampaignSerializer(data=data)
        if serializer.is_valid():
            serializer.save(created_by=user)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        
        return response.Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
    

class UpdateCampaignView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        try:
            # Fetch the campaign instance based on ID and ensure the user is the owner
            campaign = Campaign.objects.get(pk=pk, created_by=request.user)
        except Campaign.DoesNotExist:
            return response.Response({"detail": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Create a serializer instance with the existing data and the new data from the request
        serializer = CampaignSerializer(campaign, data=request.data, partial=True)
        
        # Check if the new data is valid
        if serializer.is_valid():
            serializer.save()  # Save the updated campaign instance
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        
        # If data is invalid, return the errors
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class DeleteCampaignView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            # Fetch the campaign instance and ensure the user is the owner
            campaign = Campaign.objects.get(pk=pk, created_by=request.user)
        except Campaign.DoesNotExist:
            return response.Response({"detail": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the campaign instance
        campaign.delete()
        return response.Response({"detail": "Campaign deleted successfully."}, status=status.HTTP_204_NO_CONTENT)  



class CampaignPageView(views.APIView):
    """
    View for getting campaign page views analytics. This view provides
    information on how many views the campaign page has received over time.
    """
    schema = AutoSchema()  # Automatically generates schema

    def get(self, request, campaign_id):
        """
        Get analytics of page views for a specific campaign.
        Provides the number of views per day for the specified campaign.
        """
        # Fetch the page views for the specific campaign
        page_views = CampaignPage.objects.filter(campaign_id=campaign_id) \
            .annotate(date=TruncDate('viewed_at')) \
            .values('date') \
            .annotate(views=Count('id')) \
            .order_by('date')

        # If no data found, return a 404 or empty response
        if not page_views:
            return response.Response({"message": "No data found"}, status=status.HTTP_404_NOT_FOUND)

        # Return the data serialized
        return response.Response(page_views, status=status.HTTP_200_OK)    
    

class CampaignRecommendationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        recommended_campaigns = recommend_campaigns(user_id)
        campaign_data = [{'id': campaign.id, 'name': campaign.title} for campaign in recommended_campaigns]

        return response.Response(campaign_data, status=200)    

