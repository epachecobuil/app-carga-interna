from django import forms
from .models import RegistroSesion

class RegistroSesionForm(forms.ModelForm):
    class Meta:
        model = RegistroSesion
        # Solo pedimos estos dos campos, la fecha y el usuario los pondremos en automático
        fields = ['readiness', 'rpe'] 
        
        # Le damos estilo Tailwind a los selectores desplegables
        widgets = {
            'readiness': forms.Select(attrs={
                'class': 'w-full mt-1 rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-3 border bg-slate-50'
            }),
            'rpe': forms.Select(attrs={
                'class': 'w-full mt-1 rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-3 border bg-slate-50'
            })
        }