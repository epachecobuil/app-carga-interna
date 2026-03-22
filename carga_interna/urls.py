from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from autorreg import views as autorreg_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='autorreg/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', autorreg_views.registro_usuario, name='registro'),
    
    # 1. El Hub Principal (ahora es la página de inicio)
    path('', autorreg_views.hub_principal, name='hub'),
    
    # 2. Herramienta de Carga Interna
    path('carga-interna/', autorreg_views.panel_deportista, name='panel_carga'),
]