from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_fuerza, name='panel_fuerza'),
]