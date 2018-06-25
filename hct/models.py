import mimetypes

import sys
from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser, PermissionsMixin, AbstractBaseUser
from django.core.files.base import ContentFile

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save, pre_delete, post_save
from django.db.models import F, Case, When


from django.utils import timezone
from django.utils.text import slugify

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
import os


def image_location(instance, filename):
    return "media_cdn/imagenes/%s-%s" %(instance.nombre, filename)

def thumb_location(instance, filename):
    return "media_cdn/thumbnails/%s-%s" %(instance.nombre, filename)


class Foto(models.Model):
    nombre = models.CharField(max_length=120)
    archivo = models.ImageField(upload_to=image_location)
    thumbnail = models.ImageField(upload_to=thumb_location, max_length=500, null=True, blank=True)

    def __str__(self):
        return self.nombre

    def __unicode__(self):
        return self.nombre


    def create_thumbnail(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.archivo:
            return



        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (120, 120)

        DJANGO_TYPE = self.archivo.file.content_type

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'

        # Open original photo which we want to thumbnail using PIL's Image
        archivo = Image.open(BytesIO(self.archivo.read()))

        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.
        archivo.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = BytesIO()
        archivo.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(self.archivo.name)[-1],
                temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.thumbnail.save(
            '%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf,
            save=False
        )

    def save(self, *args, **kwargs):

        self.create_thumbnail()

        force_update = False

        # If the instance already has been saved, it has an id and we set
        # force_update to True
        if self.id:
            force_update = True

        # Force an UPDATE SQL query if we're editing the image to avoid integrity exception
        super(Foto, self).save(force_update=force_update)

class Subasta(models.Model):
    titulo = models.CharField(max_length=120)
    precio = models.FloatField()
    slug = models.SlugField(unique=True)
    publicacion = models.DateTimeField(null=True)
    descripcion = models.TextField(max_length=700)
    fecha_limite = models.DateTimeField(null=True)
    vendedor = models.ForeignKey(AUTH_USER_MODEL, blank=False, related_name='user_vendedor')
    tiene_img = models.BooleanField(default=False)
    imagenes = models.ManyToManyField(Foto)
    maxpujador = models.ForeignKey(AUTH_USER_MODEL, null=True, related_name='user_pujador')

    def __str__(self):
        return self.titulo

    def __unicode__(self):
        return self.titulo

    @property
    def estado(self):
        if self.publicacion:
            tiempo = self.fecha_limite - timezone.now()

            if tiempo.days < 0:
                return "finalizado"
            else:
                return "publicado"
        else:
            return "oculto"

    @property
    def tiempo_restante(self):

        tiempo = self.fecha_limite - timezone.now()
        dias, segundos = tiempo.days, tiempo.seconds
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos = segundos % 60

        return "%s dias, %s horas, %s minutos" %(dias, horas, minutos)

    def get_absolute_url(self):
        return reverse("subastas:detalles", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["-publicacion"]



#Funciones


#FOTO

def pre_delete_foto_receiver(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    if instance.archivo:
        if os.path.isfile(instance.archivo.path):
            os.remove(instance.archivo.path)
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)

#SUBASTA
def create_slug(instance, new_slug=None):
    slug = slugify(instance.titulo)
    if new_slug is not None:
        slug = new_slug

    qs = Subasta.objects.filter(slug=slug).order_by("-id")
    existe = qs.exists()
    if existe:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug



def pre_save_subasta_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


#CONFIGURACIÓN
pre_save.connect(pre_save_subasta_receiver, sender=Subasta)
pre_delete.connect(pre_delete_foto_receiver, sender=Foto)

