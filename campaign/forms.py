from django import forms
from .models import Campaign,Backer

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'image', 'goal_amount']



class BackerForm(forms.ModelForm):
    class Meta:
        model = Backer
        fields = ['pledged_amount', 'reward']  

class CreateCampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'goal_amount', 'category_type', 'image', 'video', 'start_date', 'deadline']              
        