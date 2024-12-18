from django.urls import path
from . import views

urlpatterns = [
    path('donations/user-update/<int:donation_id>/', views.UserUpdateDonationView.as_view()),
    path('donations/<int:campaign_id>/', views.CreateDonationView.as_view()), 
    path('make-donation/', views.MakeDonationView.as_view()),
    path('campaigns/<int:campaign_id>/funding-trends/', views.FundingTrendsView.as_view()),
    path('admin/reports/platform-revenue/', views.PlatformRevenueView.as_view()),
    path('admin/reports/user-activity/', views.UserActivityView.as_view()),
    path('admin/reports/total-campaigns/', views.TotalCampaignsView.as_view()),
    path('admin/reports/total-donations/', views.TotalDonationsView.as_view()),
    
    
]