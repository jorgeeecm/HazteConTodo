import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf.global_settings import AUTH_USER_MODEL

# Create your views here.

#GESTION DE USUARIOS

#Ver perfil de usuario
from .forms import ProfileForm
from .models import Perfil

def ver_perfil(request, nombre=None):


    user = get_object_or_404(User, username=nombre)

    profile = user.perfil

    context = {
        "profile": profile,
    }

    return render(request, "ver_perfil.html", context)


#Editar perfil
@login_required
def editar_perfil(request, nombre):

    if nombre == None:
        messages.error(request, "No existe un usuario con este nombre")
        return redirect("subastas:home")

    user = get_object_or_404(User, username=nombre)

    if user != request.user:
        messages.error(request, "Solo puede editar su perfil")
        return redirect("subastas:home")

    form = ProfileForm(request.POST or None, request.FILES or None, instance=user.perfil)
    if form.is_valid():
        with transaction.atomic():
            profile = form.save(commit=False)

            if request.FILES:
                profile.avatar = request.FILES.get('input-file')

            user.first_name = request.POST.get('nombre')
            user.last_name = request.POST.get('apellido')

            user.save()
            profile.save()

            messages.success(request, "El perfil de usuario ha sido modificado")
        return redirect("usuarios:ver_perfil", nombre=nombre)

    context = {
        "usuario": user,
        "form": form
    }

    return render(request, "editar_perfil.html", context)
