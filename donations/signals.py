# We want to trigger a signal when a new contribution is made to a campaign
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Donation
from django.utils import timezone
from django.apps import apps

@receiver(post_save, sender=Donation)
def send_donation_notification(sender, instance, created, **kwargs):
    if created:  # Only trigger when a new contribution is made (not an update)
        donor = instance.donor
        campaign = instance.campaign
        amount = instance.amount
        
        # Notify the campaign creator (owner)
        if campaign.created_by != donor:  # Don't notify the contributor about their own contribution
            send_donation_email(campaign.created_by, campaign, donor, amount)

        # Optionally, notify the contributor as well
        send_donation_email(donor, campaign, donor, amount)

def send_donation_email(recipient, campaign, donor, amount):
    """
    Helper function to send an email notification about a contribution.
    """
    subject = f"New Donation to Your Campaign: {campaign.title}"
    message = f"Dear {recipient.first_name},\n\n" \
              f"You've received a donation of {amount} from {donor.first_name} to your campaign '{campaign.title}'.\n" \
              f"Current funding: {campaign.get_total_donations()}/{campaign.goal_amount}\n" \
              f"Thank you for your support!\n\nBest regards,\nThe Campaign Team"  
    
    send_mail(
        subject,
        message,
        'no-reply@yourapp.com', 
        [recipient.email], 
        fail_silently=False,
    )


@receiver(post_save, sender=Donation)
def check_campaign_funding_goal(sender, instance, created, **kwargs):
    if created:  # Trigger only for new donations
        campaign = instance.campaign
        
        # Check if the campaign has reached or exceeded its funding goal
        if campaign.get_total_donations() >= campaign.goal_amount:  # Check if the current funding has met or exceeded the goal
            send_funding_goal_achieved_email(campaign.created_by, campaign)

def send_funding_goal_achieved_email(recipient, campaign):
    """
    Helper function to send an email when the funding goal is achieved.
    """
    subject = f"Congratulations! Your campaign '{campaign.title}' has reached its funding goal!"
    message = f"Dear {recipient.first_name},\n\n" \
              f"Congratulations! Your campaign '{campaign.title}' has successfully reached its funding goal of {campaign.goal_amount}.\n" \
              f"Total raised: {campaign.get_total_donations()}\n\n" \
              f"Thank you for your hard work, and best of luck with your project!\n\nBest regards,\nThe Campaign Team"  
    
    send_mail(
        subject,
        message,
        'no-reply@yourapp.com',  # From email
        [recipient.email],  # To email
        fail_silently=False,
    )
