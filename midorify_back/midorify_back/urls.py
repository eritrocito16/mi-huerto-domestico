"""
URL configuration for midorify_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.shortcuts import redirect

from django.contrib import admin
from django.urls import path, include
from huerto_app.views import login_view, dashboard_view, mis_plantas_view, cuidados_view, historial_view, registro_view, registrar_cuidado_view,confirmar_cuidado_view, notificaciones_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('huerto_app.api.urls')), 
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('mis-plantas/', mis_plantas_view, name='mis_plantas'),
    path('cuidados/', cuidados_view, name='cuidados'),
    path('historial/', historial_view, name='historial'),
    path('registro/', registro_view, name='registro'),
    path('notificaciones/', notificaciones_view, name='notificaciones'),

    path('', lambda request: redirect('/login/')),
    path('registrar-cuidado/', registrar_cuidado_view),
    path('confirmar_cuidado/', confirmar_cuidado_view),



]
