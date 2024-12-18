#  it’s designed to suggest campaigns to users based on their donation history, particularly the categories they’ve donated to in the past.

from collections import Counter
from profiles.models import UserProfile
from.models import Campaign
from donations.models import Donation

def get_user_profile(user_id):
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return {}
    
    donations = Donation.objects.filter(donor=user_profile.user)
    categories = []

    for donation in donations:
        categories.extend(donation.campaign.categories.values_list('name', flat=True))
    return dict(Counter(categories))


def recommend_campaigns(user_id):
    user_profile = get_user_profile(user_id)
    user_interested_categories = set(user_profile.keys())

    recommended_camapigns = []

    for campaign in Campaign.objects.all():
        common_categories = user_interested_categories.intersection(
            set(campaign.categories.values_list('name',flat=True))
        )
        if common_categories:
            recommended_camapigns.append(campaign)


    return recommended_camapigns        
        