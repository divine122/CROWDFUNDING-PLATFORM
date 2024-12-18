# To allow API consumers (e.g., admins or other services) to view the activity logs, you can create a viewset and use Django REST Framework’s router.

from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import LogbookViewSet

router = DefaultRouter()
router.register(r'activity-logs', LogbookViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]