from django.urls import path
from . import views

urlpatterns = [
     path('campaigns/<int:campaign_id>/comments/add/', views.CreateCommentView.as_view()),  
     path('comments/', views.CommentListView.as_view()),
     path('comments/<int:comment_id>/moderate/', views.CommentModerationView.as_view()),
     path('comments/<int:comment_id>/delete/', views.CommentDeleteView.as_view()),
    
    

    

]