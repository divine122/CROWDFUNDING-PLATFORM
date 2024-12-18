from django.db import models
from django.conf import settings

# Create your models here.


VERIFICATION_CHOICES = [
    ('APPROVED','APPROVED'),
    ('REJECTED','REJECTED'),
    ('PENDING','PENDING'),
]

class KYC(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verification_status = models.CharField(max_length=59, choices= VERIFICATION_CHOICES)

    def __str__(self):
        return f"KYC for  ({self.verification_status})"