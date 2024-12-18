from django.db import models

from django.conf import settings

class Donation(models.Model):
    campaign = models.ForeignKey('campaign.Campaign', on_delete=models.CASCADE)
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null= True)


    def __str__(self):
        return f"Donation of {self.amount}  for {self.campaign.title}"

class DonationGoal(models.Model):
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_donated = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Goal: {self.goal_amount}, Total Donated: {self.total_donated}"