from django.urls import path

from . import views

urlpatterns = [
     path('users/me/', views.UserProfileView.as_view()),
]
