from django import forms
from .models import RegistroSesion

READINESS_RPE_CHOICES = [(i, i) for i in range(1, 11)]

class RegistroSesionForm(forms.ModelForm):
    readiness = forms.ChoiceField(
        choices=READINESS_RPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full mt-1 rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-3 border bg-slate-50'
        })
    )
    rpe = forms.ChoiceField(
        choices=READINESS_RPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full mt-1 rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-3 border bg-slate-50'
        })
    )

    class Meta:
        model = RegistroSesion
        # AÑADIMOS 'duracion_minutos' A LA LISTA
        fields = ['readiness', 'rpe', 'duracion_minutos'] 
        
        widgets = {
            'duracion_minutos': forms.NumberInput(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-3 border bg-slate-50', 'min': '1', 'max': '300'})
        }