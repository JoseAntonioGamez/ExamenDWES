from django.contrib import admin
from .models import Estudio, Videojuego, Sede,Plataforma, Analisis

# Register your models here.

admin.site.register(Estudio)
admin.site.register(Videojuego)
admin.site.register(Sede)
admin.site.register(Plataforma)
admin.site.register(Analisis)