from django import forms
from .models import Ejercicio, SesionFuerza

class EjercicioForm(forms.ModelForm):
    class Meta:
        model = Ejercicio
        fields = ['nombre', 'enlace_video']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50'}),
            'enlace_video': forms.URLInput(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50', 'placeholder': 'https://youtube.com/...'}),
        }

class SesionFuerzaForm(forms.ModelForm):
    class Meta:
        model = SesionFuerza
        # Ya no hay rastro de 'duracion_minutos' aquí
        fields = ['fecha', 'ejercicio', 'kilos', 'series', 'repeticiones']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50'}),
            'ejercicio': forms.Select(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50'}),
            'kilos': forms.NumberInput(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50', 'step': '0.5'}),
            'series': forms.NumberInput(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50'}),
            'repeticiones': forms.NumberInput(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50'}),
        }

    class Meta:
        model = SesionFuerza
        fields = ['fecha', 'ejercicio', 'kilos', 'series', 'repeticiones']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50'}),
            'ejercicio': forms.Select(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50'}),
            'kilos': forms.NumberInput(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50', 'step': '0.5'}),
            'series': forms.NumberInput(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50'}),
            'repeticiones': forms.NumberInput(attrs={'class': 'w-full mt-1 rounded-md border-slate-300 p-2 border bg-slate-50'}),
        }