from django.urls import path, re_path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ej1/', views.ejercicio1, name='ejercicio1'),
    path('ej2/', views.ejercicio2, name='ejercicio2'),
    path('ej3/', views.ejercicio3, name='ejercicio3'),
    path('ej4/<int:anio>/', views.ejercicio4, name='ejercicio4'),
    path('ej5/<int:centro_id>/', views.ejercicio5, name='ejercicio5'),
]