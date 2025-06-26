from rest_framework import viewsets
from huerto_app.models import Usuario
from huerto_app.api.serializers import UsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
