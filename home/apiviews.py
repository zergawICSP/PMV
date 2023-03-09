from django.shortcuts import render,redirect
from rest_framework import viewsets
from . models import Client

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('-id')