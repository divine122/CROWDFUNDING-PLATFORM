from django.urls import path
from . import views

urlpatterns = [
    path('campaign-view/', views.CampaignView, name='campaign_view'),  
    path('create-campaign/', views.CreateCampaignView, name='create_campaign'),  
    path('campaign-update/<int:pk>/', views.UpdateCampaignView, name='update_campaign'),  
    path('campaign-delete/<int:pk>/', views.DeleteCampaignView, name='delete_campaign'),
    path('recommendations/', views.CampaignRecommendationView, name='campaign_recommendation'),   
    path('campaigns/<int:campaign_id>/page-views/', views.CampaignPageView, name='campaign_page_view'), 
]

