from django.contrib import admin


# Register your models here.
from usuarios.models import Perfil

class ProfileAdmin(admin.ModelAdmin):
    list_display = ["__str__", "usuario", "localidad"]
    class Meta:
        model = Perfil

admin.site.register(Perfil, ProfileAdmin)
