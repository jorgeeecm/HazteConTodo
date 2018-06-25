import os
import sys

from django.conf.global_settings import AUTH_USER_MODEL
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from PIL import Image
from io import BytesIO

from hct.models import Subasta


def user_image_location(instance, filename):
    return "media_cdn/usuarios/imagenes/%s-%s" %(instance.usuario, filename)


def user_thumb_location(instance, filename):
    return "media_cdn/usuarios/thumbnail/%s" %(filename)

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    pujas = models.ManyToManyField(Subasta, blank=True)
    avatar = models.ImageField(upload_to=user_image_location, blank=True, null=True)
    avatar_thumb = models.ImageField(upload_to=user_thumb_location, blank=True, null=True)
    localidad = models.CharField(max_length=30, blank=True, null=True)
    comunidad = models.CharField(max_length=30, blank=True, null=True)
    descripcion = models.TextField(max_length=700, blank=True, null=True)

    def __str__(self):
        return self.usuario.username


    def save(self, *args, **kwargs):
        if self.avatar:
            img = Image.open(BytesIO(self.avatar.read()))
            thumb = img.resize((96, 96), Image.ANTIALIAS)
            temp_handle = BytesIO()

            if img.format == 'JPEG':
                content = 'image/jpeg'
                thumb.save(temp_handle, format='JPEG')
            elif img.format == 'PNG':
                content = 'image/png'
                thumb.save(temp_handle, format='PNG')


            temp_handle.seek(0)
            filename = "%s_thumbnail.%s" % (self.avatar.name.split('.')[0], img.format)

            if self.avatar_thumb:
                if os.path.isfile(self.avatar_thumb.path):
                    os.remove(self.avatar_thumb.path)

                self.avatar_thumb.delete(save=False)

            #change the imagefield value to be the newley modifed image value
            self.avatar_thumb = InMemoryUploadedFile(temp_handle,'ImageField', filename, content, sys.getsizeof(temp_handle), None)

        super(Perfil, self).save(*args, **kwargs)


User.perfil = property(lambda u: Perfil.objects.get_or_create(usuario=u)[0])


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.perfil.save()

#Funciones

#PROFILE

def pre_delete_profile_receiver(sender, instance, *args, **kwargs ):

    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)

    if instance.avatar_thumb:
        if os.path.isfile(instance.avatar_thumb.path):
            os.remove(instance.avatar_thumb.path)


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
post_save.connect(create_user_profile, sender=AUTH_USER_MODEL)
post_save.connect(save_user_profile, sender=AUTH_USER_MODEL)

pre_delete.connect(pre_delete_profile_receiver, sender=Perfil)
#pre_delete.connect(pre_delete_profile_receiver, sender=Perfil)

