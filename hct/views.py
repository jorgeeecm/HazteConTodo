import datetime

import os
from allauth.account.decorators import verified_email_required
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q

from haztecontodo.settings import EMAIL_HOST_USER
from .models import Subasta, Foto
from .forms import SubastaForm


#Email
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

# Create your views here.


#Redirección para usuarios
def redireccion (request):

    return HttpResponseRedirect("subastas:home")

#Actualizar subasta - AJAX
def actualizar_subasta(request, slug):
    subasta = get_object_or_404(slug=slug)
    variables = {
        'subasta': subasta,
        'urls': request.urls,
    }
    return render(request, "detalles.html", variables)
#Home
def subasta_home(request):

    subastas = [obj for obj in Subasta.objects.all() if obj.estado == "publicado"]

    paginator = Paginator(subastas, 6) #6 subastas por pagina
    page = request.GET.get('pagina')
    try:
       subastas_p = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        subastas_p = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        subastas_p = paginator.page(paginator.num_pages)

    variables = {
        "subastas": subastas_p,

    }

    return render(request, "home.html",variables)

#Ordenar subastas
def ordenar_subastas(request, opcion=None):

    subastas = subastas_opcion(opcion)

    if subastas == None:
        messages.error(request, "Seleccione una opción valida")
        return redirect("subastas:home")

    paginator = Paginator(subastas, 6) #Mostramos 6 subastas por pagina
    page = request.GET.get('pagina')
    try:
       subastas_p = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        subastas_p = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        subastas_p = paginator.page(paginator.num_pages)

    variables = {
        "subastas": subastas_p,

    }

    return render(request, "home.html",variables)


#Función que hace de switch-case
def subastas_opcion(opcion):
    subastas = [obj for obj in Subasta.objects.all() if obj.estado == "publicado"]
    return {
        'foto': [obj for obj in subastas if obj.tiene_img == True],
        'chollos': sorted(subastas, key=lambda a: a.precio, reverse=False),
        'ultimas': sorted(subastas, key=lambda a: a.tiempo_restante, reverse=False),
    }.get(opcion, None)    # 9 is default if x not found

#Buscar subastas
def buscar_subastas(request):

    if request.POST:
        if request.POST.get('condicion2'):
            condicion = request.POST.get('condicion2')

        if request.POST.get('condicion'):
           condicion = request.POST.get('condicion')

        subastas = Subasta.objects.filter(Q(titulo__icontains=condicion) | Q(descripcion__icontains=condicion))
        subastas = [obj for obj in subastas if obj.estado == "publicado"]

        if subastas:
            paginator = Paginator(subastas, 6) #Mostramos 6 subastas por pagina
            page = request.GET.get('pagina')
            try:
               subastas_p = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                subastas_p = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                subastas_p = paginator.page(paginator.num_pages)

            variables = {
                "subastas": subastas_p,

            }

            return render(request, "home.html", variables)

        messages.warning(request, "No hemos encontrado ninguna subasta")
        return redirect("subastas:home")

    else:
        messages.warning(request, "Realice las busquedas utilizando la herramienta preparada para ello")
        return redirect("subastas:home")

#Ver subasta
def obtener_subasta(request, slug=None):


    subasta = get_object_or_404(Subasta, slug=slug)

    imagenes = subasta.imagenes.all()
    urls = []

    if imagenes:
        for img in imagenes:
            urls.append(img.archivo.url)

    variables = {
        "subasta": subasta,
        "urls": urls,
    }

    return render(request, "detalles.html", variables)

#Crear subasta
#@verified_email_required
@transaction.atomic
def crear_subasta(request):

    form = SubastaForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        subasta = form.save(commit=False)
        subasta.vendedor = request.user

        subasta.save()

        #Recorremos los archivos y creamos una instancia para cada uno
        if request.FILES:
            subasta.tiene_img = True
            for imagen in request.FILES.getlist('input-file'):
                f = Foto.objects.create(archivo=imagen, nombre=subasta.titulo)
                #Foto(archivo=imagen, nombre=subasta.titulo).save()
                subasta.imagenes.add(Foto.objects.get(id=f.id))

            subasta.save()

        messages.success(request, "Subasta publicada correctamente")
        return HttpResponseRedirect(subasta.get_absolute_url())

    context = {
        "form": form,
    }

    return render(request, "crear_subasta.html", context)

#Modificar/publicar subasta
@verified_email_required
@transaction.atomic
def modificar_subasta(request, slug=None):

    subasta = get_object_or_404(Subasta, slug=slug)

    if not request.user == subasta.vendedor:
        messages.error(request, "No tiene permiso para modificar esta subasta")
        return redirect("subastas:home")

    form = SubastaForm(request.POST or None, request.FILES or None, instance=subasta)
    if form.is_valid():
        with transaction.atomic():
            subasta = form.save(commit=False)

            if request.FILES:
                subasta.tiene_img = True
                #obtenemos las fotos relacionadas con la subasta
                fotos = subasta.imagenes.all()


                #Eliminamos todos las fotos anteriores
                for i in fotos:
                    i.delete()

                #Rompemos la relacion
                subasta.imagenes.clear()

                #Creamos y asignamos las nuevas
                for imagen in request.FILES.getlist('input-file'):
                    f = Foto.objects.create(archivo=imagen, nombre=subasta.titulo)
                    subasta.imagenes.add(Foto.objects.get(id=f.id))

            if ('guardar' in request.POST):

                messages.success(request, "Los cambios han sido guardados")
            elif ('publicar' in request.POST):
                subasta.publicacion = timezone.now()
                subasta.fecha_limite = timezone.now() + datetime.timedelta(days=int(request.POST.get('dias')), hours=int(request.POST.get('horas')))

                enviar_mail(request.user, subasta, "Subasta publicada")
                messages.success(request, "La subasta ha sido publicada")

            subasta.save()
        return HttpResponseRedirect(subasta.get_absolute_url())

    imagenes = subasta.imagenes.all()
    urls = []

    for img in imagenes:
        urls.append(img.thumbnail.url)

    context = {
        "subasta": subasta,
        "form": form,
        "imagenes": urls,

    }

    return render(request, "editar_subasta.html", context)

#Eliminar subasta
@verified_email_required
def eliminar_subasta(request, slug=None):

    subasta = get_object_or_404(Subasta, slug=slug)

    if request.user == subasta.vendedor:
        context = {
        "subasta": subasta,
        }
        return render(request, "eliminar_subasta.html", context)


    messages.error(request, "No tiene permiso para eliminar esta subasta")
    return redirect("subastas:home")



@verified_email_required
@transaction.atomic
def eliminar_conf(request, slug):

    subasta = get_object_or_404(Subasta, slug=slug)

    if not request.user == subasta.vendedor or not request.user.is_staff:
        messages.error(request, "No tiene permiso para eliminar esta subasta")
        return redirect("subastas:home")

    with transaction.atomic():
        #Eliminamos una a una las fotos relacionadas con la subasta
        if (subasta.tiene_img):
            imagenes = subasta.imagenes.all()
            for img in imagenes:
                img.delete()

        subasta.delete()
        messages.success(request, "La subasta se elimino correctamente")
    return redirect("subastas:home")


#Subastas de un usuario
@login_required
def mis_subastas(request, opcion=None):

    subastas = selector_subastas(request,opcion)

    if( subastas == None):
        messages.error(request, "No ha especificado un tipo estado valido de subasta")
        return redirect("subastas:home")
    else:
        if not subastas:
            context = {
                "opcion": opcion,
            }
            return render(request,"sin_subastas.html", context)
        else:
            paginator = Paginator(subastas, 6) # Show 3 contacts per page
            page = request.GET.get('pagina')
            try:
               subastas_p = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                subastas_p = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                subastas_p = paginator.page(paginator.num_pages)

            variables = {
                "subastas": subastas_p,
                "opcion": opcion,
            }

            return render(request, "mis_subastas.html", variables)


#Función que hace de switch-case
def selector_subastas(request, opcion):
    return {
        'publicas': [obj for obj in Subasta.objects.filter(vendedor=request.user) if obj.estado == "publicado"],
        'ocultas': [obj for obj in Subasta.objects.filter(vendedor=request.user) if obj.estado == "oculto"],
        'finalizadas': [obj for obj in Subasta.objects.filter(vendedor=request.user) if obj.estado == "finalizado"],
    }.get(opcion, None)    # 9 is default if x not found


#Pujar una subasta
@verified_email_required
def pujar(request, slug=None):

    subasta = get_object_or_404(Subasta, slug=slug)

    if request.user == subasta.vendedor:
        messages.warning(request, "No puedes pujar en tus propias subastas")
        return redirect("subastas:home")

    if (request.POST.get('puja') == None):
        messages.warning(request, "Por favor, puje de la manera correcta")
        return redirect("subastas:detalles", subasta.slug)
    else:
        precio = float(request.POST.get('puja'))

    if subasta.estado == "publicado":
        with transaction.atomic():
            if (precio > subasta.precio) :
                subasta.precio = precio
                antiguo_usuario = subasta.maxpujador

                subasta.maxpujador = request.user

                #Comprobamos si ya ha relizado una puja sobre la subasta, para que no haya duplicados
                pujas = request.user.perfil.pujas.all()
                if not subasta in pujas:
                    request.user.perfil.pujas.add(subasta)


                subasta.save()
                if antiguo_usuario:
                    if not antiguo_usuario == request.user:
                        enviar_mail(antiguo_usuario, subasta, "Puja superada")

                enviar_mail(request.user,subasta,"Puja realizada")

            else:
                messages.error(request, "El precio de su puja es inferior al precio actual de la puja")

        return redirect("subastas:detalles", subasta.slug)

    messages.error(request, "La subasta no esta activa, no se puede realizar la puja")
    return redirect("subastas:home")


#Ver mis pujas
@login_required
def mis_pujas(request):
    pujas = request.user.perfil.pujas.all()

    variables = {
        "pujas": pujas,
    }

    return render(request, "mis_pujas.html", variables)



def prueba(request, slug):

    subasta = get_object_or_404(Subasta, slug=slug)

    variables = {
        'subasta': subasta,
        'precio': subasta.precio,
        'tiempo': subasta.tiempo_restante,
    }

    return render(request, "prueba.html", variables)

def objeto_ajax(request, slug):
    if request.is_ajax():
        subasta = get_object_or_404(Subasta, slug=slug)
        variables = {
            'precio': subasta.precio,
            'tiempo': subasta.tiempo_restante,
        }


        print("ENTRA AJAX")
        return JsonResponse(variables)


#-------------------EMAIL----------------------
#Función para mandar email

def enviar_mail(usuario, subasta, opcion):

    mail = usuario.email
    objeto = subasta

    if(opcion == "Puja realizada"):

        texto = render_to_string(
            'mensajes/email_puja_realizada.html', {
                'email': mail,
                'subasta': objeto,
            },
        )

    elif (opcion == "Puja superada"):

         texto = render_to_string(
            'mensajes/email_puja_superada.html', {
                'email': mail,
                'subasta': objeto,
            },
        )

    elif (opcion == "Subasta publicada"):
         texto = render_to_string(
            'mensajes/email_subasta_publicada.html', {
                'email': mail,
                'subasta': objeto,
            },
        )

    email_message = EmailMessage(
        subject=opcion,
        body=texto,
        from_email=EMAIL_HOST_USER,
        to=(mail,),
    )

    email_message.content_subtype = 'html'
    email_message.send()

    return 0





