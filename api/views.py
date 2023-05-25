from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework import viewsets
from home.models import Client
from .serializers import ClientSerializer

class ClientViewSet(viewsets.ModelViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Client.objects.all().order_by('-id')
    serializer_class = ClientSerializer
    