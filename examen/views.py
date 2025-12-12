from datetime import datetime
from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import *
from django.db.models import Q, Avg, Count, Max, Min, Prefetch
from django.db.models.functions import Length
from django.shortcuts import render
from django.views.defaults import page_not_found
from .forms import *
from django.contrib.auth import login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseForbidden
from .forms import EnsayoClinicoForm, BusquedaAvanzadaEnsayoForm
from django.contrib import messages


# Create your views here.

def index(request):
    if(not "fecha_inicio" in request.session):
        request.session["fecha_inicio"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.user.is_authenticated:
        if not "nombre" in request.session:
            request.session["nombre"] = request.user.username
        if not "rol" in request.session:
            
            try:
                request.session["rol"] = dict(Usuario.ROLES)[request.user.rol]
            except Exception:
                request.session["rol"] = None
        if not "visitas" in request.session:
            request.session["visitas"] = 0
        request.session["visitas"] = request.session["visitas"] + 1

    return render(request, 'index.html')


def registrar_usuario(request):
    tipo = request.GET.get('tipo') or request.POST.get('tipo')
    if tipo == 'paciente':
        FormClass = RegistroPacienteForm
    else:
        
        FormClass = RegistroInvestigadorForm

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro completado')
            return redirect('index')
    else:
        form = FormClass()

    return render(request, 'registration/signup.html', {'formulario': form, 'tipo': tipo})


def logout_view(request):
    request.session.flush()
    auth_logout(request)
    return redirect('index')

def ensayo_create(request):
    datosFormulario = None
    if request.method == 'POST':
        datosFormulario = request.POST
    formulario = EnsayoClinicoForm(datosFormulario)
    
    if (request.method == "POST"):
        ensayo_creado = crear_ensayo_modelo(formulario)
        if (ensayo_creado):
            messages.success(request, 'Ensayo clínico creado exitosamente.')
            return redirect('lista_ensayos')
    return render(request, 'ensayos/crear_ensayo.html', {"formulario": formulario}) 
            
def crear_ensayo_modelo(formulario):
    ensayo_creado = False
    if formulario.is_valid():
        try:
            formulario.save()
            ensayo_creado = True
        except:
            pass
    return ensayo_creado


def registro_investigador(request):
    if request.method == 'POST' and request.POST.get('tipo') == 'investigador':
        form = RegistroInvestigadorForm(request.POST)
    elif request.method == 'POST':
        form = RegistroInvestigadorForm(request.POST)
    else:
        form = RegistroInvestigadorForm()

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Registro de investigador completado')
        return redirect('index')

    return render(request, 'registration/signup.html', {'formulario': form, 'tipo': 'investigador'})


@permission_required('examen.view_ensayoclinico')
def lista_ensayos(request):
    form = BusquedaAvanzadaEnsayoForm(request.GET or None)
    qs = EnsayoClinico.objects.all()

    investigador = Investigador.objects.filter(usuario=request.user).first()
    paciente = Paciente.objects.filter(usuario=request.user).first()
    if investigador:
        qs = qs.filter(creado_por=investigador)
    elif paciente:
        qs = qs.filter(pacientes=paciente)

    if form.is_valid():
        texto = form.cleaned_data.get('textoBusqueda')
        fdesde = form.cleaned_data.get('fecha_inicio_desde')
        fhasta = form.cleaned_data.get('fecha_inicio_hasta')
        nivel_min = form.cleaned_data.get('nivel_seguimiento_min')
        pacientes = form.cleaned_data.get('pacientes')
        solo_activos = form.cleaned_data.get('solo_activos')

        if texto:
            qs = qs.filter(Q(nombre__icontains=texto) | Q(descripcion__icontains=texto))
        if fdesde:
            qs = qs.filter(fecha_inicio__gte=fdesde)
        if fhasta:
            qs = qs.filter(fecha_inicio__lte=fhasta)
        if nivel_min is not None:
            qs = qs.filter(nivel_seguimiento__gt=nivel_min)
        if pacientes:
            qs = qs.filter(pacientes__in=pacientes).distinct()
        if solo_activos:
            qs = qs.filter(activo=True)

    return render(request, 'ensayos/lista_ensayos.html', {'ensayos': qs, 'form': form})


@permission_required('examen.add_ensayoclinico')
def crear_ensayo(request):
    investigador = Investigador.objects.filter(usuario=request.user).first()
    if not investigador:
        investigador = Investigador.objects.create(usuario=request.user, nombre=request.user.username)

    if request.method == 'POST':
        form = EnsayoClinicoForm(request.POST)
        if form.is_valid():
            ensayo = form.save(usuario=request.user)
            messages.success(request, 'Ensayo clínico creado exitosamente.')
            return redirect('detalle_ensayo', ensayo_id=ensayo.pk)
    else:
        form = EnsayoClinicoForm()

    return render(request, 'ensayos/crear_ensayo.html', {'form': form})


@permission_required('examen.view_ensayoclinico')
def detalle_ensayo(request, ensayo_id):
    ensayo = get_object_or_404(EnsayoClinico, pk=ensayo_id)
    investigador = Investigador.objects.filter(usuario=request.user).first()
    paciente = Paciente.objects.filter(usuario=request.user).first()

    allowed = False
    if investigador and ensayo.creado_por == investigador:
        allowed = True
    elif paciente and ensayo.pacientes.filter(pk=paciente.pk).exists():
        allowed = True
    elif request.user.is_superuser:
        allowed = True

    if not allowed:
        return HttpResponseForbidden('No tienes permiso para ver este ensayo')

    return render(request, 'ensayos/detalle_ensayo.html', {'ensayo': ensayo})


@permission_required('examen.change_ensayoclinico')
def editar_ensayo(request, ensayo_id):
    ensayo = get_object_or_404(EnsayoClinico, pk=ensayo_id)
    investigador = Investigador.objects.filter(usuario=request.user).first()
    if not investigador or ensayo.creado_por != investigador:
        return HttpResponseForbidden('Solo el investigador creador puede editar este ensayo')

    if request.method == 'POST':
        form = EnsayoClinicoForm(request.POST, instance=ensayo)
        if form.is_valid():
            form.save(usuario=request.user)
            messages.success(request, 'Ensayo actualizado')
            return redirect('detalle_ensayo', ensayo_id=ensayo.pk)
    else:
        form = EnsayoClinicoForm(instance=ensayo)

    return render(request, 'ensayos/editar_ensayo.html', {'form': form, 'ensayo': ensayo})


@permission_required('examen.delete_ensayoclinico')
def eliminar_ensayo(request, ensayo_id):
    ensayo = get_object_or_404(EnsayoClinico, pk=ensayo_id)
    investigador = Investigador.objects.filter(usuario=request.user).first()
    if not investigador or ensayo.creado_por != investigador:
        return HttpResponseForbidden('Solo el investigador creador puede eliminar este ensayo')

    if request.method == 'POST':
        ensayo.delete()
        messages.success(request, 'Ensayo eliminado')
        return redirect('lista_ensayos')

    return render(request, 'ensayos/confirmar_eliminar.html', {'ensayo': ensayo})




"""
Manejo de errores personalizados
"""



def mi_error_400(request, exception=None):
    return render(request, 'errores/400.html', None, None, 400)

def mi_error_403(request, exception=None):
    return render(request, 'errores/403.html', None, None, 403)

def mi_error_404(request, exception=None):
    return render(request, 'errores/404.html', None, None, 404)

def mi_error_500(request):
    return render(request, 'errores/500.html', None, None, 500)


