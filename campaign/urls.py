from django.urls import path
from . import views

urlpatterns = [
    path('campaign-view/', views.CampaignView.as_view()),  
    path('create-campaign/', views.CreateCampaignView.as_view()),  
    path('campaign-update/<int:pk>/', views.UpdateCampaignView.as_view()),  
    path('campaign-delete/<int:pk>/', views.DeleteCampaignView.as_view()),
    path('recommendations/', views.CampaignRecommendationView.as_view()),   
    path('campaigns/<int:campaign_id>/page-views/', views.CampaignPageView.as_view()), 
]

