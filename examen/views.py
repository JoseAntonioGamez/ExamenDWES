from django.shortcuts import render
from .models import *
from django.db.models import Avg, Max, Min, Q, Prefetch
from django.views.defaults import page_not_found


# Create your views here.


def index(request):
    return render(request, 'index.html') 

"""
Ejercicio1
"""

def listar_videojuegos(request):
    """
    videojuegos = (Videojuego.objects.raw("SELECT "
        +    "V.*,E.*,VP.*,P.*"
        +"FROM" 
        +   "examen_videojuego V"
        +"INNER JOIN"
        +    "examen_estudio E ON V.estudio_desarrollo_id = E.id"
        +"INNER JOIN"
        +    "examen_sede S ON E.id = S.estudio_id"
        +"LEFT JOIN" 
        +    "examen_videojuego_plataformas VP ON V.id = VP.videojuego_id"
        +"LEFT JOIN"
        +    "examen_plataforma P ON VP.plataforma_id = P.id"
        +"LEFT JOIN"
        +    "examen_analisis A ON V.id = A.videojuego_id"
        +"WHERE" 
        +    "V.titulo LIKE '%Fantasy%'" 
        +    "AND S.pais LIKE '%unidos%'")
    )
    """
    
    videojuegos=Videojuego.objects.filter(
        titulo__icontains='Fantasy',
        estudio_desarrollo__sedes__pais__icontains='Unidos').select_related('estudio_desarrollo').prefetch_related('videojuego_plataformas__plataforma').prefetch_related('analisis').distinct()

    
    return render(request, 'urls/unidos_fantasy.html', {'videojuegos': videojuegos})

def mi_error_400(request, exception=None):
    return render(request, 'errores/400.html', None, None, 400)

def mi_error_403(request, exception=None):
    return render(request, 'errores/403.html', None, None, 403)

def mi_error_404(request, exception=None):
    return render(request, 'errores/404.html', None, None, 404)

def mi_error_500(request):
    return render(request, 'errores/500.html', None, None, 500)