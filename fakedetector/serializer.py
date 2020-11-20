from .models import Noticia
from rest_framework import serializers

class NoticiaSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(required=False,allow_blank=True,max_length=100)
    cuerpo =  serializers.CharField(required=True,allow_blank=False,max_length=99999)
    fecha = serializers.DateField(required=False)
    idioma = serializers.CharField(required=False,allow_blank=False,max_length=20)
    
    class Meta:
        model = Noticia
        fields = ['titulo','cuerpo','fecha','prediccion','idioma']

