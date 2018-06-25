from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^verperfil/(?P<nombre>[\w-]+)/$', ver_perfil, name="ver_perfil"),
    url(r'^editarperfil/(?P<nombre>[\w-]+)/$', editar_perfil, name="editar_perfil"),

]
