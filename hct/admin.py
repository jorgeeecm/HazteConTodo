from django.contrib import admin

# Register your models here.
from .models import Subasta,Foto

class SubastaAdmin(admin.ModelAdmin):
    list_display = ["__str__", "vendedor", "publicacion"]
    list_filter = ["publicacion"]
    search_fields = ["titulo", "descripcion"]
    class Meta:
        model = Subasta

class FotoAdmin(admin.ModelAdmin):
    list_display = ["__str__", "archivo"]
    class Meta:
        model = Foto

admin.site.register(Subasta, SubastaAdmin)
admin.site.register(Foto, FotoAdmin)
