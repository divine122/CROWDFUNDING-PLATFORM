from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from rest_framework import status,views,permissions,response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from decimal import  Decimal
from django.db import transaction
from django.db.models.functions import TruncDate
from django.db.models import Sum
from django.db.models import Count
from django.contrib.auth.models import User
from django.apps import apps

from campaign.models import Campaign
from . models import Donation,DonationGoal
from. serializers import DonationSerializer,UserUpdateDonationSerializer

# Create your views here.

class DonationCreateView(views.APIView):
    queryset = Donation.objects.all()  # Get all donations
    serializer_class = DonationSerializer  # Use the Donation serializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can donate

    def perform_create(self, serializer):
        # Automatically associate the logged-in user with the donation
        user = self.request.user
        
        # Get the campaign ID from the request data
        campaign_id = self.request.data.get("campaign")
        
        # Ensure a campaign is specified
        if not campaign_id:
           return response.Response(
                        {"error": "Campaign is required"},
                        status=status.HTTP_403_FORBIDDEN
                    )

        
        try:
            # Check if the campaign exists
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
          return response.Response(
                        {"error": "Invalid Campaign"},
                        status=status.HTTP_403_FORBIDDEN
                    )


        # Now we save the donation, including the user (donor) and campaign
        serializer.save(donor=self.request.user, campaign=campaign)



class UserUpdateDonationView(views.APIView):
   permission_classes = [permissions.IsAuthenticated]
   serializer_class = UserUpdateDonationSerializer


   @swagger_auto_schema(request_body=UserUpdateDonationSerializer)
   def put(self, request, donation_id):
        """
     Update a donation for a crowdfunding campaign.

        This view allows a user to update their donation amount and message.
        """
        user = request.user  # Get the current logged-in user
        data = request.data  # Retrieve input data from the request

        try:
            # Retrieve the donation by its ID
            donation = Donation.objects.get(id=donation_id)

            # Check if the donation belongs to the logged-in user (donor)
            if donation.donor != self.request.user:
                raise PermissionDenied("You can only update your own donation.")

            # Extract data from the request
            amount = data.get('amount', donation.amount)  # Amount, default to current value if not provided
            message = data.get('message', donation.message)  # Message, default to current value if not provided

            # Validate amount (make sure it's a positive value)
            if Decimal(amount) <= 0:
                return response.Response(
                    {"error": "Donation amount must be greater than zero."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate the message (optional, if provided)
            # Here you can add custom validation if needed, e.g., length checks

            # Use the Donation serializer to validate the updated data
            donation_data = {
                'amount': amount,
                'message': message,
                'donor': user.id,
                'campaign': donation.campaign.id  # Keep the same campaign
            }

            serializer = UserUpdateDonationSerializer(donation, data=donation_data)

            # Check if serializer is valid
            if not serializer.is_valid():
                return response.Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update the donation fields directly without using a transaction block
            donation.amount = Decimal(amount)
            donation.message = message
            donation.save()

            # Optionally, you can add additional actions like creating a notification, etc.
            # For example: Notification.objects.create(user=user, remark="Donation updated", amount=amount)

            # Save the updated donation using the serializer
            serializer.save()

            # Return the updated donation data
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        except Donation.DoesNotExist:
            # Handle case where the donation doesn't exist
            return response.Response(
                {"error": "Donation does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return response.Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            # Catch other unexpected errors
            return response.Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class CreateDonationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=DonationSerializer)  # Ensure this is using the right serializer
    def post(self, request, campaign_id, *args, **kwargs):
        campaign = Campaign.objects.get(id=campaign_id)
        amount = request.data.get("amount")

        # Check if 'amount' is provided and valid
        if amount is None:
            return response.Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)  # Ensure the amount is converted to a float
        except ValueError:
            return response.Response({"detail": "Amount must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return response.Response({"detail": "Contribution amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed to create the donation if everything is valid
        donation = Donation.objects.create(
            donor=request.user,
            campaign=campaign,
            amount=amount
        )

        return response.Response({"detail": "Contribution successful."}, status=status.HTTP_201_CREATED)


class MakeDonationView(views.APIView):

    @swagger_auto_schema(request_body=DonationSerializer)
    def post(self, request, *args, **kwargs):
        # Deserialize the incoming data
        serializer = DonationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Start a database transaction to ensure atomicity
            with transaction.atomic():
                # Save the donation
                donation = serializer.save()
                campaign = donation.campaign

                campaign.raised_amount += donation.amount
                campaign.save()

                # # Update the total donated amount
                # donation_goal = DonationGoal.objects.first()  # Assuming one goal for simplicity
                # if donation_goal:
                #     donation_goal.total_donated += donation.amount
                #     donation_goal.save()

                return response.Response({
                    "message": "Donation successful",
                    "donation": serializer.data,
                    "raised_amount": str(campaign.raised_amount),
                    "goal_amount": str(campaign.goal_amount),
                }, status=status.HTTP_201_CREATED)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  




class FundingTrendsView(views.APIView):
    """
    View to get funding trends for a specific campaign.
    This endpoint returns the total donation amount per day for the campaign.
    """
    @swagger_auto_schema()
    def get(self, request, campaign_id):
        """
        Get funding trends for a specific campaign. This returns the total donation amount
        per day for the campaign.
        """
        # Fetch donations for the given campaign and aggregate by day
        donations = Donation.objects.filter(campaign_id=campaign_id) \
            .annotate(date=TruncDate('timestamp')) \
            .values('date') \
            .annotate(total_amount=Sum('amount')) \
            .order_by('date')

        # Return a 404 if no donations are found
        if not donations:
            return response.Response({"message": "No data found for the given campaign"}, status=status.HTTP_404_NOT_FOUND)

        # Return the aggregated data (total donations per day)
        return response.Response(donations, status=status.HTTP_200_OK)



class PlatformRevenueView(views.APIView):
    """
    View to get platform revenue (total donations across all campaigns).
    """
    @swagger_auto_schema()
    def get(self, request):
        # Calculate total donations across all campaigns
        total_revenue = Donation.objects.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        return response.Response({"platform_revenue": total_revenue}, status=status.HTTP_200_OK) 

class UserActivityView(views.APIView):
    """
    View to get user activity (number of donations, number of campaigns created).
    """
    @swagger_auto_schema()
    def get(self, request):

        UserModel = apps.get_model(settings.AUTH_USER_MODEL)
        # Get all users with their donation count and campaign creation count
        user_activity =UserModel.objects.annotate(  # Use custom user model
            donation_count=Count('donation'),
            campaign_count=Count('campaign')
        ).values('first_name', 'donation_count', 'campaign_count')

        return response.Response(user_activity, status=status.HTTP_200_OK)

class TotalCampaignsView(views.APIView):
    """
    View to get the total number of campaigns in the platform.
    """
    @swagger_auto_schema()
    def get(self, request):
        # Count total campaigns
        total_campaigns = Campaign.objects.count()

        return response.Response({"total_campaigns": total_campaigns}, status=status.HTTP_200_OK) 


class TotalDonationsView(views.APIView):
    """
    View to get the total number of donations made across all campaigns.
    """
    @swagger_auto_schema()
    def get(self, request):
        # Count total donations
        total_donations = Donation.objects.count()

        return response.Response({"total_donations": total_donations}, status=status.HTTP_200_OK)               