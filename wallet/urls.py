from django.urls import path
from .import views

urlpatterns = [
    path('wallet-detail/', views.WalletDetailView.as_view()),
    path('wallet-deposite/', views.WalletDepositView.as_view()),
    path('wallet-withdrawal/', views.WalletWithdrawalView.as_view())
]