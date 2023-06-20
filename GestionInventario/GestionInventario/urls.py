"""
URL configuration for GestionInventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from AppGestionInventario import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [ 
    path('admin/', admin.site.urls),
    #path('vistaInicio/',views.vistaInicio),
    path('Login/',views.login),
    path('vistaRegistrarUsuario/',views.vistaRegistrarUsuario),
    path('registrarUsuario/',views.registrarUsuario),  
    path('ListarUsuarios/',views.ListarUsuarios),
    path('LoginVista/',views.vistaLogin),
    path('vistaRegistrarDevolutivo/',views.vistaRegistrarDevolutivo),
    path('registrarDevolutivo/',views.registrarDevolutivo),
    path('vistaGestionarDevolutivos/',views.vistaGestionarDevolutivos),
    path('registrarMaterial/',views.registrarMaterial),
    path('vistaRegistrarMaterial/',views.vistaRegistrarMaterial),
    path('vistaEntradaMaterial/',views.vistaEntradaMaterial),
    path('registrarEntradaMaterial/',views.registrarEntradaMaterial),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)