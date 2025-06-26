from rest_framework import serializers
from huerto_app.models import Usuario 

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'