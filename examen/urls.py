from django.urls import path, re_path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ej1/', views.ejercicio1, name='ejercicio1'),
    path('ej2/', views.ejercicio2, name='ejercicio2')
]