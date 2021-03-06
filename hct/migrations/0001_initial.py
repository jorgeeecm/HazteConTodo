# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-02 11:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hct.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Foto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120)),
                ('archivo', models.ImageField(upload_to=hct.models.image_location)),
                ('thumbnail', models.ImageField(blank=True, max_length=500, null=True, upload_to=hct.models.thumb_location)),
            ],
        ),
        migrations.CreateModel(
            name='Subasta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=120)),
                ('precio', models.FloatField()),
                ('slug', models.SlugField(unique=True)),
                ('publicacion', models.DateTimeField(null=True)),
                ('descripcion', models.TextField(max_length=700)),
                ('fecha_limite', models.DateTimeField(null=True)),
                ('tiene_img', models.BooleanField(default=False)),
                ('imagenes', models.ManyToManyField(to='hct.Foto')),
                ('maxpujador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_pujador', to=settings.AUTH_USER_MODEL)),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_vendedor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-publicacion'],
            },
        ),
    ]
