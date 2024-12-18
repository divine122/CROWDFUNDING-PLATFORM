from django.urls import path
from . import views


urlpatterns = [
    path('kyc/',views.KYCView.as_view() ),
    path('kyc-update/', views.KycUpdateView.as_view()),
    path('kyc-detail/', views.KYCDetailView.as_view())
]