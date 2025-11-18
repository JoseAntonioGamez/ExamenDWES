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
def ejercicio1(request):
    animales = Animal.objects.filter(
        nombre__icontains='Max',
        centro__refugio__nombre='Animales_Felices'
    ).select_related('centro', 'centro__refugio').prefetch_related(
        'animal_vacunas__vacuna'
    ).distinct()
    return render(request, 'urls/ejercicio1.html', {'animales': animales})

"""
Ejercicio2
"""
def ejercicio2(request):
    animales = Animal.objects.filter(
        Q(animal_vacunas__vacuna__fabricante__icontains='Zoetis'),
        Q(animal_vacunas__vacuna__nombre__icontains='Rabia'),
        revisiones__puntuacion_salud__gt=80
    ).select_related('centro'
    ).prefetch_related('animal_vacunas__vacuna'
    ).distinct()[:3]
    return render(request, 'urls/ejercicio2.html', {'animales': animales})


"""
Ejercicio3
"""
def ejercicio3(request):
    animales = Animal.objects.filter(animal_vacunas=None).select_related('centro'
    ).order_by('-edad_estimada').distinct()
    return render(request, 'urls/ejercicio3.html', {'animales': animales})


"""
Ejercicio4
"""
def ejercicio4(request, anio):
    refugios = Refugio.objects.filter(
        centros__animales__revisiones__fecha__year=anio
    ).order_by('-centros__animales__revisiones__puntuacion_salud'
    ).distinct()
    return render(request, 'urls/ejercicio4.html', {'refugios': refugios, 'anio': anio})


"""
Ejercicio5
"""


"""
Ejercicio6
"""


def mi_error_400(request, exception=None):
    return render(request, 'errores/400.html', None, None, 400)

def mi_error_403(request, exception=None):
    return render(request, 'errores/403.html', None, None, 403)

def mi_error_404(request, exception=None):
    return render(request, 'errores/404.html', None, None, 404)

def mi_error_500(request):
    return render(request, 'errores/500.html', None, None, 500)