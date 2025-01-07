from django.shortcuts import render

# Create your views here.

from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone

from .models import Campaign,CampaignPage,Backer
from rest_framework import status,permissions,response,views
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser,FormParser
from django.db.models import Count
from rest_framework.schemas import AutoSchema
from django.db.models.functions import TruncDate
from .engines import recommend_campaigns
from rest_framework.decorators import action
from.forms import CampaignForm,BackerForm,CreateCampaignForm
from django.http import HttpResponseBadRequest
from django.contrib import messages

# class CampaignView(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = CampaignSerializer
#     parser_classes = (MultiPartParser, FormParser)


#     @swagger_auto_schema(request_body=CampaignSerializer)
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             # Assign the current user to the created_by field
#             campaign = serializer.save(created_by=request.user)
#             return response.Response({"message": "Campaign created successfully", "project": campaign.id}, status=201)
#         return response.Response(serializer.errors, status=400)

#     @swagger_auto_schema(request_body=BackerSerializer)
#     @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
#     def add_backer(self, request, *args, **kwargs):
#         """Add a backer to the campaign"""
#         campaign_id = kwargs.get('pk')  # Get campaign ID from URL
#         campaign = Campaign.objects.get(id=campaign_id)

#         pledged_amount = request.data.get('pledged_amount')
#         reward = request.data.get('reward', None)  # optional field for reward
#         user = request.user  # The user backing the campaign

#         if not pledged_amount:
#             return response.Response({"error": "Pledged amount is required."}, status=status.HTTP_400_BAD_REQUEST)

#         # Create the backer record
#         backer = Backer.objects.create(
#             user=user,
#             campaign=campaign,
#             pledged_amount=pledged_amount,
#             reward=reward
#         )

#         # You may want to update the campaign's raised amount
#         campaign.update_goal(pledged_amount)

#         return response.Response(BackerSerializer(backer).data, status=status.HTTP_201_CREATED)

def home_page(request):
    return render(request, 'home.html') 

class CampaignView:
    def get(self, request, campaign_id):
        # Retrieve the campaign by its ID or show a 404 error if not found
        campaign = get_object_or_404(Campaign, id=campaign_id)
        
        # Render the campaign detail template with the campaign object
        return render(request, 'campaign_detail.html', {'campaign': campaign})
        
class AddBackerView:
    def get(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, id=campaign_id)
        form = BackerForm()
        return render(request, 'add_backer.html', {'form': form, 'campaign': campaign})

    def post(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, id=campaign_id)
        form = BackerForm(request.POST)
        
        if form.is_valid():
            pledged_amount = form.cleaned_data.get('pledged_amount')
            reward = form.cleaned_data.get('reward')

            if pledged_amount <= 0:
                messages.error(request, "Pledged amount must be greater than zero.")
                return render(request, 'add_backer.html', {'form': form, 'campaign': campaign})

            # Create the backer record
            backer = Backer.objects.create(
                user=request.user,
                campaign=campaign,
                pledged_amount=pledged_amount,
                reward=reward
            )

            # Update the campaign's goal amount
            campaign.update_goal(pledged_amount)

            messages.success(request, f"Successfully backed the campaign with ${pledged_amount}.")
            return redirect('campaign_detail', campaign_id=campaign.id)
        else:
            return render(request, 'add_backer.html', {'form': form, 'campaign': campaign})        



   

# class CreateCampaignView(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = CreateCampaignSerializer 
   

#     @swagger_auto_schema(request_body=CampaignSerializer)
#     def post(self,request):
#         user = request.user
#         data = request.data
#         if Campaign.objects.filter(created_by=user , status= 'active').exists():
#             return response.Response(
#                 {'error':'you alraedy have an active campaign'},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#         serializer = CampaignSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save(created_by=user)
#             return response.Response(
#                 serializer.data, status=status.HTTP_201_CREATED
#             )
        
#         return response.Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


class CreateCampaignView:
    def get(self, request):
        # Render the form for creating a campaign
        form = CreateCampaignForm()
        return render(request, 'create_campaign.html', {'form': form})

    def post(self, request):
        # Handle form submission
        form = CreateCampaignForm(request.POST, request.FILES)  # Handle file uploads if needed
        if form.is_valid():
            user = request.user
            
            # Check if the user already has an active campaign
            if Campaign.objects.filter(created_by=user, status='active').exists():
                messages.error(request, 'You already have an active campaign.')
                return render(request, 'create_campaign.html', {'form': form})

            # Assign the current user to the created_by field and save the campaign
            campaign = form.save(commit=False)
            campaign.created_by = user
            campaign.save()
            
            messages.success(request, 'Campaign created successfully!')
            return redirect('campaign_detail', campaign_id=campaign.id)  # Redirect to the campaign detail page or list page
            
        else:
            return render(request, 'create_campaign.html', {'form': form})
    

# class UpdateCampaignView(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def patch(self, request, pk, *args, **kwargs):
#         try:
#             # Fetch the campaign instance based on ID and ensure the user is the owner
#             campaign = Campaign.objects.get(pk=pk, created_by=request.user)
#         except Campaign.DoesNotExist:
#             return response.Response({"detail": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND)
        
#         # Create a serializer instance with the existing data and the new data from the request
#         serializer = CampaignSerializer(campaign, data=request.data, partial=True)
        
#         # Check if the new data is valid
#         if serializer.is_valid():
#             serializer.save()  # Save the updated campaign instance
#             return response.Response(serializer.data, status=status.HTTP_200_OK)
        
#         # If data is invalid, return the errors
#         return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class UpdateCampaignView:
    def get(self, request, campaign_id):
        # Retrieve the campaign by its ID or show a 404 error if not found
        campaign = get_object_or_404(Campaign, id=campaign_id)

        # Check if the user is the creator of the campaign
        if campaign.created_by != request.user:
            messages.error(request, 'You are not authorized to edit this campaign.')
            return redirect('campaign_detail')  # Redirect to a safe page (e.g., campaign list)

        # If the user is authorized, show the form with the campaign data
        form = CampaignForm(instance=campaign)
        return render(request, 'update_campaign.html', {'form': form, 'campaign': campaign})

    def post(self, request, campaign_id):
        # Retrieve the campaign by its ID or show a 404 error if not found
        campaign = get_object_or_404(Campaign, id=campaign_id)

        # Check if the user is the creator of the campaign
        if campaign.created_by != request.user:
            messages.error(request, 'You are not authorized to edit this campaign.')
            return redirect('campaign_detail')  # Redirect to a safe page (e.g., campaign list)

        # If the user is authorized, handle the form submission
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            # Save the updated campaign
            form.save()
            messages.success(request, 'Campaign updated successfully!')
            return redirect('campaign_detail', campaign_id=campaign.id)  # Redirect to the campaign's detail page or any other page
        else:
            return render(request, 'update_campaign.html', {'form': form, 'campaign': campaign})

# class DeleteCampaignView(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def delete(self, request, pk, *args, **kwargs):
#         try:
#             # Fetch the campaign instance and ensure the user is the owner
#             campaign = Campaign.objects.get(pk=pk, created_by=request.user)
#         except Campaign.DoesNotExist:
#             return response.Response({"detail": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Delete the campaign instance
#         campaign.delete()
#         return response.Response({"detail": "Campaign deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
# 
# 


class DeleteCampaignView:
    def get(self, request, campaign_id):
        # Retrieve the campaign by its ID or show a 404 error if not found
        campaign = get_object_or_404(Campaign, id=campaign_id)

        # Check if the user is the creator of the campaign
        if campaign.created_by != request.user:
            messages.error(request, 'You are not authorized to delete this campaign.')
            return redirect('campaign_list')  # Redirect to a safe page

        # Render a confirmation page to delete the campaign
        return render(request, 'confirm_delete_campaign.html', {'campaign': campaign})

    def post(self, request, campaign_id):
        # Retrieve the campaign by its ID or show a 404 error if not found
        campaign = get_object_or_404(Campaign, id=campaign_id)

        # Check if the user is the creator of the campaign
        if campaign.created_by != request.user:
            messages.error(request, 'You are not authorized to delete this campaign.')
            return redirect('campaign_detail')  # Redirect to a safe page

        # Delete the campaign
        campaign.delete()
        messages.success(request, 'Campaign deleted successfully!')
        
        # Redirect to the campaign list or another appropriate page
        return redirect('campaign_detail')  # Replace 'campaign_list' with the correct U



# class CampaignPageView(views.APIView):
#     """
#     View for getting campaign page views analytics. This view provides
#     information on how many views the campaign page has received over time.
#     """
#     schema = AutoSchema()  # Automatically generates schema

#     def get(self, request, campaign_id):
#         """
#         Get analytics of page views for a specific campaign.
#         Provides the number of views per day for the specified campaign.
#         """
#         # Fetch the page views for the specific campaign
#         page_views = CampaignPage.objects.filter(campaign_id=campaign_id) \
#             .annotate(date=TruncDate('viewed_at')) \
#             .values('date') \
#             .annotate(views=Count('id')) \
#             .order_by('date')

#         # If no data found, return a 404 or empty response
#         if not page_views:
#             return response.Response({"message": "No data found"}, status=status.HTTP_404_NOT_FOUND)

#         # Return the data serialized
#         return response.Response(page_views, status=status.HTTP_200_OK)    


class CampaignPageView:
    """
    View to display campaign page details and allow users to interact with it (e.g., make pledges).
    """
    def get(self, request, campaign_id):
        # Fetch the campaign by its ID or return a 404 if not found
        campaign = get_object_or_404(Campaign, id=campaign_id)

        # Fetch campaign page views if needed (for analytics or tracking purposes)
        page_views = CampaignPage.objects.filter(campaign_id=campaign_id) \
            .annotate(date=TruncDate('viewed_at')) \
            .values('date') \
            .annotate(views=Count('id')) \
            .order_by('date')

        # Render the campaign page with the campaign details, views, and a message if needed
        return render(request, 'campaign_page.html', {
            'campaign': campaign,
            'page_views': page_views  # Passing the page views data to the template
        })

    def post(self, request, campaign_id):
        # Fetch the campaign by its ID or return a 404 if not found
        campaign = get_object_or_404(Campaign, id=campaign_id)

        # Check if the user is trying to back their own campaign
        if request.user == campaign.created_by:
            messages.error(request, "You cannot back your own campaign.")
            return redirect('campaign_page', campaign_id=campaign.id)

        # Get the pledged amount and reward (if any) from the POST data
        pledged_amount = request.POST.get('pledged_amount')
        reward = request.POST.get('reward')

        if not pledged_amount:
            messages.error(request, "Pledge amount is required.")
            return redirect('campaign_page', campaign_id=campaign.id)

        # Create a new Backer record
        Backer.objects.create(
            user=request.user,
            campaign=campaign,
            pledged_amount=pledged_amount,
            reward=reward
        )

        # Optionally, update the campaign's raised amount (if needed)
        campaign.raised_amount += float(pledged_amount)
        campaign.save()

        # Create a page view entry if needed (analytics tracking)
        CampaignPage.objects.create(
            user=request.user,
            campaign=campaign,
            viewed_at=timezone.now()  # Use timezone-aware datetime
        )

        messages.success(request, 'Thank you for backing the campaign!')

        # Redirect back to the campaign page
        return redirect('campaign_page', campaign_id=campaign.id)
    

# class CampaignRecommendationView(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         user_id = request.user.id
#         recommended_campaigns = recommend_campaigns(user_id)
#         campaign_data = [{'id': campaign.id, 'name': campaign.title} for campaign in recommended_campaigns]

#         return response.Response(campaign_data, status=200)    

class CampaignRecommendationView:
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get the user ID of the logged-in user
        user_id = request.user.id
        
        # Get the recommended campaigns using the recommend_campaigns function from engine.py
        recommended_campaigns = recommend_campaigns(user_id)
        
        # Prepare the campaign data to send to the template
        campaign_data = [{'id': campaign.id, 'name': campaign.title} for campaign in recommended_campaigns]

        # Render the HTML page with the recommended campaigns
        return render(request, 'campaign_recommendations.html', {'campaigns': campaign_data})

