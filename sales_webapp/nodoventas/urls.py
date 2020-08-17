from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("<str:casa_id>", views.casa, name="casa"),
    path("altacliente/", views.cliente, name="altacliente"),
    path("cliente_<str:cliente_id>/", views.modifcliente, name="modifcliente"),
    path("listaclientes/", views.listaclientes, name="listaclientes"),
    path("casas_<str:nom_calle>/", views.lista_porcalle, name="lista_porcalle"),
    path("estado_<str:nom_estado>/", views.lista_porestado, name="lista_porestado"),
    path("media/<str:carpeta>/<str:archivo>", views.documentos, name="documentos"),
    path("errorcliente_<str:cliente_id>/", views.error_cliente, name="errorcliente"),
    path("", views.casadefault, name="casadefault"),
    path("seguimientocliente/", views.seguimientocliente, name="seguimientocliente"),
    path("logout/", views.logout_view, name="logout_view"),
    path("listaseguimientocliente/", views.listaseguimientocliente, name="listaseguimientocliente")
]
