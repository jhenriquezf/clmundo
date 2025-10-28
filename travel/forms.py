from django import forms
from .models import Incident
from django.utils import timezone

class MagicLinkForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': 'tu@email.com'
        })
    )

class OTPForm(forms.Form):
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': '+56 9 1234 5678'
        })
    )
    otp_code = forms.CharField(
        max_length=6,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': '123456'
        })
    )

class IncidentReportForm(forms.ModelForm):
    """Formulario para reportar incidencias por parte del cliente"""
    
    class Meta:
        model = Incident
        fields = ['title', 'description', 'category', 'severity', 'location', 
                 'incident_datetime', 'reporter_contact', 'affected_passengers']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Título del problema (ej: Bus llegó tarde)',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Describe detalladamente qué ocurrió...',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'severity': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ubicación donde ocurrió (opcional)'
            }),
            'incident_datetime': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'type': 'datetime-local'
            }),
            'reporter_contact': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Tu teléfono de contacto (opcional)'
            }),
            'affected_passengers': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '1',
                'value': '1'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer datetime por defecto
        if not self.instance.pk:
            self.fields['incident_datetime'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')

class IncidentResolutionForm(forms.ModelForm):
    """Formulario para que el staff resuelva incidencias"""
    
    class Meta:
        model = Incident
        fields = ['status', 'resolution_notes', 'internal_notes', 'assigned_to', 'requires_followup']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': 4,
                'placeholder': 'Descripción de la solución aplicada...'
            }),
            'internal_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': 3,
                'placeholder': 'Notas internas para el equipo...'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'requires_followup': forms.CheckboxInput(attrs={
                'class': 'rounded text-blue-600 focus:ring-blue-500'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar usuarios staff en assigned_to
        from django.contrib.auth.models import User
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)
        self.fields['assigned_to'].empty_label = "Sin asignar"

class CustomerSatisfactionForm(forms.ModelForm):
    """Formulario para calificación del cliente"""
    
    class Meta:
        model = Incident
        fields = ['customer_satisfaction']
        widgets = {
            'customer_satisfaction': forms.RadioSelect(choices=[
                (1, '⭐ Muy insatisfecho'),
                (2, '⭐⭐ Insatisfecho'),
                (3, '⭐⭐⭐ Neutral'),
                (4, '⭐⭐⭐⭐ Satisfecho'),
                (5, '⭐⭐⭐⭐⭐ Muy satisfecho'),
            ], attrs={
                'class': 'space-y-2'
            })
        }