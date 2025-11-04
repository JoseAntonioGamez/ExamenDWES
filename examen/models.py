from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Estudio(models.Model):
    nombre = models.CharField(max_length=100)
    
class Sede(models.Model):
    estudio = models.ForeignKey(Estudio, on_delete=models.CASCADE, related_name='sedes')
    pais = models.CharField(max_length=100)

class Plataforma(models.Model):
    nombre = models.CharField(max_length=100)
    fabricante = models.CharField(max_length=100)

class Videojuego(models.Model):
    titulo = models.CharField(max_length=200)
    estudio_desarrollo = models.ForeignKey(Estudio, on_delete=models.CASCADE, related_name='videojuegos')
    ventas_estimadas = models.IntegerField(null=True, blank=True)

class VideojuegoPlataformas(models.Model):
    videojuego = models.ForeignKey(Videojuego, on_delete=models.CASCADE, related_name='videojuego_plataformas')
    plataforma = models.ForeignKey(Plataforma, on_delete=models.CASCADE, related_name='plataformas_videojuegos')

class Analisis(models.Model):
    videojuego = models.ForeignKey(Videojuego, on_delete=models.CASCADE, related_name='analisis')
    puntuacion = models.IntegerField(default=50)
    comentario = models.TextField(null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
