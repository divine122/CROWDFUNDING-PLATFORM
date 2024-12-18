from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Logbook
from .serializers import LogbookSerializer

class LogbookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Logbook.objects.all()
    serializer_class = LogbookSerializer
