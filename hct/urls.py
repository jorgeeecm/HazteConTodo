from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^$', subasta_home, name="home"),
    url(r'^crear/$', crear_subasta, name="crear"),
    url(r'^ajax/(?P<slug>[\w-]+)/$', objeto_ajax, name="ajax"),
    url(r'^mispujas/$', mis_pujas, name="mis_pujas"),
    url(r'^buscar/$', buscar_subastas, name="buscar"),
    url(r'^ordenar/(?P<opcion>[\w-]+)/$', ordenar_subastas, name="ordenar"),
    url(r'^missubastas/(?P<opcion>[\w-]+)/$', mis_subastas, name="mis_subastas"),
    url(r'^actualizar_subasta/(?P<slug>[\w-]+)/$', actualizar_subasta, name="actualizar"),
    url(r'^(?P<slug>[\w-]+)/$', obtener_subasta, name="detalles"),
    url(r'^(?P<slug>[\w-]+)/pujar/$', pujar, name="pujar"),
    url(r'^(?P<slug>[\w-]+)/editar/$', modificar_subasta, name="editar"),
    url(r'^(?P<slug>[\w-]+)/eliminar/$', eliminar_subasta, name="eliminar"),
    url(r'^(?P<slug>[\w-]+)/eliminar/conf/$', eliminar_conf, name="eliminar_conf"),

]
