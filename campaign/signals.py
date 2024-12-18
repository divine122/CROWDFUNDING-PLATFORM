from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Backer
from django.core.mail import send_mail

@receiver(post_save, sender=Backer)
def send_thank_you_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Thank you for backing the campaign!',
            f"Dear {instance.user.first_name},\n\nThank you for backing the campaign '{instance.campaign.title}'. Your contribution of ${instance.pledged_amount} will help us reach our goal.",
            'no-reply@crowdfundingapp.com',
            [instance.user.email],
            fail_silently=False,
        )