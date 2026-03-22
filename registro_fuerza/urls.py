from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_fuerza, name='panel_fuerza'),
    # Ruta para editar (ejemplo: /fuerza/editar/5/)
    path('editar/<int:serie_id>/', views.editar_serie, name='editar_serie'),
]