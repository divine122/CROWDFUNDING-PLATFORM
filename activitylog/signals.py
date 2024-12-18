# Django provides signals to hook into various events, such as user login, profile updates, etc. We’ll use Django’s built-in user_logged_in signal and post_save signal to track user activities.

from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from . utils import log_activity

@receiver(user_logged_in)
def log_login_activity(user, request,sender, **kwargs):
    log_activity(user, action='login', description='User logged in')


@receiver(post_save, sender=User)
def log_profile_update(sender,instance,created,**kwargs):
    if not created:
        log_activity(instance, action='Profile update',description='User updated their profile')    
