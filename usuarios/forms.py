from django import forms

from .models import *


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            #"avatar",
            "localidad",
            "comunidad",
            "descripcion",
        ]



class SignUpForm(forms.Form):

    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    localidad = forms.CharField(max_length=30, required=False)
    pais = forms.CharField(max_length=30, required=False)

    def signup(self, request, user):
        request.user.first_name = self.cleaned_data['first_name']
        request.user.last_name = self.cleaned_data['last_name']

        up = request.user.perfil
        up.localidad = self.cleaned_data['localidad']
        up.pais = self.cleaned_data['pais']
        request.user.save()
        up.save()
