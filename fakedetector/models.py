from django.db import models

# Create your models here.
class Noticia(models.Model):
    titulo = models.CharField(blank=True,null=True,max_length=255)
    cuerpo = models.TextField()
    idioma = models.CharField(blank=True,null=True,max_length=10)
    fecha = models.DateField(null=True, blank=True, auto_now=True)
    prediccion = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return 'Noticia: {} - {}'.format(self.titulo,self.cuerpo)