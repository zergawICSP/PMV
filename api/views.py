from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from home.models import Client
from .serializers import ClientSerializer

class ClientViewSet(viewsets.ModelViewSet):

    queryset = Client.objects.all().order_by('-id')
    serializer_class = ClientSerializer

    