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


"""
Ejercicio3
"""


"""
Ejercicio4
"""


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