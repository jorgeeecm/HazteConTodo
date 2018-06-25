from django import forms

from .models import *

class SubastaForm(forms.ModelForm):
    class Meta:
        model = Subasta
        #widgets = {"vendedor": forms.HiddenInput()}
        fields = [
            "titulo",
            "precio",
            "descripcion",

        ]

    def __init__(self, *args, **kwargs):
        super(SubastaForm, self).__init__(*args, **kwargs)
        self.fields['precio'].widget.attrs['min'] = 0

class FotoForm(forms.ModelForm):
    class Meta:
        model = Foto
        fields = ("archivo", )


