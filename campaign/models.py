from django.db import models

# Create your models here.
from datetime import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from donations.models import Donation   


User = get_user_model()
# Create your models here.

STATUS_CHOICES = [
    ('ACTIVE','ACTIVE'),
    ('DRAFT','DRAFT'),
    ('COMPLETED','COMPLETED'),
    ('FAILED','FAILED')
]

CATEGORY_CHOICES = [
    ('HEALTH','HEALTH'),
    ('EDUCATION','EDUCATION'),
    ('TECHNOLOGY','TECHNOLOGY')
]

APPROVAL_STATUS_CHOICES = [
    ('APPROVED','APPROVED'),
    ('PENDING','PENDING'),
    ('REJECTED','REJECTED')
]

class Category(models.Model):
    name = models.CharField(max_length=233)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=150, choices=STATUS_CHOICES)
    category_type = models.CharField(max_length=150 , choices=CATEGORY_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(null=True, blank=True, unique=True)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2 ,default=0)
    reward = models.TextField()
    deadline = models.DateTimeField(null=True, blank=True)
    approval_status = models.CharField(max_length=17, choices=APPROVAL_STATUS_CHOICES)
    image = models.ImageField(upload_to='projects/images/', blank=True, null=True)
    video = models.FileField(upload_to='projects/videos/', blank=True, null=True)
    categories = models.ManyToManyField(Category,blank=True)

  


    def __str__(self):
        return self.title
    
    
    def update_goal(self,pledged_amount):
        self.raised_amount += pledged_amount
        self.save()

    

    def is_active(self):
        return self.status == 'ACTIVE' and self.deadline > timezone.now()
    

    def get_total_donations(self):
        return Donation.objects.filter(campaign=self).aggregate(total_donations=models.Sum('amount'))['total_donations'] or 0

    def has_reached_goal(self):
        return self.get_total_donations() >= self.goal_amount    
    


class CampaignPage(models.Model):
    campaign = models.ForeignKey('Campaign',on_delete=models.CASCADE)
    user_id = models.IntegerField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Page view for Campaign {self.campaign.id} by User {self.user_id if self.user_id else 'Anonymous'}"



class Backer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    pledged_amount = models.DecimalField(decimal_places=2, max_digits=10)
    reward = models.TextField(null=True, blank=True)
    date_backed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reward
    

    
    def save(self,*args,**kwargs,):
        self.campaign.update_goal(self.pledged_amount)
        super().save(*args, **kwargs)

