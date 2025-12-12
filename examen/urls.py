from django.urls import path, re_path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registrar', views.registrar_usuario, name='registrar_usuario'),
    path('logout/', views.logout_view, name='logout'),
    path('ensayos/', views.lista_ensayos, name='lista_ensayos'),
    path('ensayos/crear/', views.crear_ensayo, name='crear_ensayo'),
    path('ensayos/<int:ensayo_id>/', views.detalle_ensayo, name='detalle_ensayo'),
    path('ensayos/<int:ensayo_id>/editar/', views.editar_ensayo, name='editar_ensayo'),
    path('ensayos/<int:ensayo_id>/eliminar/', views.eliminar_ensayo, name='eliminar_ensayo'),


]