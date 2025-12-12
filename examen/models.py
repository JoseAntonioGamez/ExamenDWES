from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuario(AbstractUser):
    ADMINISTRADOR = 1
    PACIENTE = 2
    INVESTIGADOR = 3
    ROLES = [
        (ADMINISTRADOR, 'Administrador'),
        (PACIENTE, 'Paciente'),
        (INVESTIGADOR, 'Investigador'),
    ]

    rol = models.PositiveSmallIntegerField(
        choices=ROLES, default=1
        )

class Farmaco(models.Model):
   nombre = models.CharField(max_length=100)
   apto_para_ensayos = models.BooleanField()
   def __str__(self):
       return self.nombre
   
class EnsayoClinico(models.Model):
   nombre = models.CharField(max_length=100, unique=True)
   descripcion = models.TextField()
   farmaco = models.ForeignKey(Farmaco, on_delete=models.CASCADE)
   pacientes = models.ManyToManyField('Paciente')
   nivel_seguimiento = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
   fecha_inicio = models.DateField()
   fecha_fin = models.DateField()
   activo = models.BooleanField(default=True)
   creado_por = models.ForeignKey('Investigador', on_delete=models.CASCADE)  
   def __str__(self):
       return self.nombre
   
   def clean(self):
       # validations that should always hold
       # Intentionally avoid raising ValidationError here; form-layer will perform user-facing
       # validation and add field errors. Keep these checks as non-raising guards so
       # they can be used programmatically without throwing exceptions unexpectedly.
       if self.fecha_inicio and self.fecha_fin and self.fecha_inicio >= self.fecha_fin:
           # Invalid dates (start must be before end) -- handled in forms
           return
       from datetime import date
       if self.fecha_fin and self.fecha_fin < date.today():
           # End date in the past -- handled in forms/views for creation
           return
   
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    historial_medico = models.TextField()
    edad = models.PositiveSmallIntegerField(null=True, blank=True)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
         return self.nombre
   
class Investigador(models.Model): 
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    afiliacion_institucional = models.CharField(max_length=200)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
         return self.nombre
