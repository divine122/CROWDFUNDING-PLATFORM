from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class Logbook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=244)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.action


