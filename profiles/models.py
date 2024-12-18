from django.db import models

# Create your models here.

from django.contrib.auth import get_user_model

User = get_user_model()

GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True) 
    phone_number = models.CharField(max_length=15, blank=True, null=True)  
    image = models.ImageField(upload_to='personal-profile', blank=True)  
    date_of_birth = models.DateField(null=True, blank=True)  
    address = models.CharField(max_length=255, blank=True, null=True)  
    location = models.CharField(max_length=255, blank=True, null=True) 
    gender = models.CharField(max_length=7, choices=GENDER_CHOICES, blank=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.user.first_name

