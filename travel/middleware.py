# travel/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from .models import Customer

class EnsureCustomerMiddleware(MiddlewareMixin):
    """Asegurar que todo usuario autenticado tenga un Customer asociado"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                # Intentar acceder al customer
                customer = request.user.customer
            except Customer.DoesNotExist:
                # Crear customer automáticamente si no existe
                Customer.objects.create(
                    user=request.user,
                    phone='',
                    emergency_contact=''
                )
            except AttributeError:
                # El usuario no tiene el atributo customer (relación no configurada)
                pass
        return None