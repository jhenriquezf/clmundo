# travel/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta
from .models import Customer, Trip, TripSegment, Incident, Notification
from .forms import MagicLinkForm, OTPForm, IncidentReportForm, IncidentResolutionForm, CustomerSatisfactionForm
from .utils import generate_qr_code
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .services.google_maps import GoogleMapsService
from .services.whatsapp import WhatsAppService
import json
from django.conf import settings
from . import models
from django.contrib.auth import logout

try:
    from .services.google_maps import GoogleMapsService
    from .services.whatsapp import WhatsAppService
    
    maps_service = GoogleMapsService()
    whatsapp_service = WhatsAppService()
    
except ImportError:
    maps_service = None
    whatsapp_service = None

def magic_link_login(request):
    """Simula login con magic link - DEMO PURPOSES"""
    if request.method == 'POST':
        try:
            # Para demo, obtener o crear usuario Ana Silva automáticamente
            user, created = User.objects.get_or_create(
                username='ana.silva',
                defaults={
                    'first_name': 'Ana',
                    'last_name': 'Silva',
                    'email': 'ana.silva@email.com'
                }
            )
            
            # Crear customer si no existe
            customer, created = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'phone': '+56 9 1234 5678',
                    'emergency_contact': 'Pedro Silva +56 9 8765 4321'
                }
            )
            
            # IMPORTANTE: Hacer login usando Django's login function
            login(request, user)
            
            # Mensaje de confirmación
            messages.success(request, f'¡Bienvenida {user.first_name}!')
            
            # Redirigir a home
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Error en el login: {str(e)}')
            return redirect('landing')
    
    return redirect('landing')

@login_required
def download_voucher(request, segment_id):
    """Descargar voucher como imagen QR"""
    customer = get_object_or_404(Customer, user=request.user)
    segment = get_object_or_404(TripSegment, id=segment_id, trip__customer=customer)
    
    # Datos para el QR
    qr_data = {
        'voucher_code': segment.voucher_code,
        'service': segment.service.name,
        'date': segment.scheduled_datetime.strftime('%Y-%m-%d %H:%M'),
        'customer': customer.user.get_full_name(),
        'location': segment.pickup_location
    }
    
    qr_image = generate_qr_code(str(qr_data))
    
    # En un entorno real, aquí generarías un PDF o imagen
    # Por ahora retornamos los datos del QR
    return JsonResponse({
        'voucher_code': segment.voucher_code,
        'qr_image': qr_image,
        'service': segment.service.name
    })

@login_required 
def notifications_list(request):
    """Lista de notificaciones del usuario"""
    customer = get_object_or_404(Customer, user=request.user)
    notifications = customer.notifications.all()[:10]
    
    # Marcar como leídas
    customer.notifications.filter(read=False).update(read=True)
    
    context = {
        'notifications': notifications
    }
    return render(request, 'travel/notifications.html', context)

@csrf_exempt
@login_required
def get_directions(request, segment_id):
    """Obtener direcciones para llegar al punto de encuentro"""
    customer = get_object_or_404(Customer, user=request.user)
    segment = get_object_or_404(TripSegment, id=segment_id, trip__customer=customer)
    
    # En un entorno real, aquí integrarías con Google Maps API
    directions_data = {
        'destination': segment.pickup_location,
        'estimated_time': '15 minutos',
        'distance': '2.3 km',
        'directions': [
            'Salir del hotel hacia el sur',
            'Girar a la derecha en Av. Costanera',
            'Continuar 500m hasta el punto de encuentro'
        ]
    }
    
    return JsonResponse(directions_data)

def landing_page(request):
    """Página de bienvenida con opciones de login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    context = {
        'magic_link_form': MagicLinkForm(),
        'otp_form': OTPForm(),
    }
    return render(request, 'travel/landing.html', context)

@login_required
def home(request):
    """Página principal con itinerario del día"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        # Si por alguna razón no existe customer, crearlo
        customer = Customer.objects.create(
            user=request.user,
            phone='',
            emergency_contact=''
        )
    
    today = date.today()
    
    # Buscar viaje activo
    active_trip = Trip.objects.filter(
        customer=customer,
        start_date__lte=today,
        end_date__gte=today
    ).first()
    
    if not active_trip:
        # Buscar próximo viaje
        active_trip = Trip.objects.filter(
            customer=customer,
            start_date__gt=today
        ).first()
    
    today_segments = []
    upcoming_segments = []
    
    if active_trip:
        # Segmentos de hoy
        today_segments = TripSegment.objects.filter(
            trip=active_trip,
            scheduled_datetime__date=today
        ).order_by('scheduled_datetime')
        
        # Próximos segmentos (siguientes 3 días)
        upcoming_segments = TripSegment.objects.filter(
            trip=active_trip,
            scheduled_datetime__date__gt=today,
            scheduled_datetime__date__lte=today + timedelta(days=3)
        ).order_by('scheduled_datetime')[:3]
    
    # Notificaciones no leídas
    try:
        unread_notifications = customer.notifications.filter(read=False).count()
    except:
        unread_notifications = 0
    
    context = {
        'customer': customer,
        'active_trip': active_trip,
        'today_segments': today_segments,
        'upcoming_segments': upcoming_segments,
        'unread_notifications': unread_notifications,
        'today': today,
        'current_language': request.LANGUAGE_CODE,
    }
    return render(request, 'travel/home.html', context)

@login_required
def segment_detail(request, segment_id):
    """Detalle de un segmento del viaje"""
    customer = get_object_or_404(Customer, user=request.user)
    segment = get_object_or_404(TripSegment, id=segment_id, trip__customer=customer)
    
    context = {
        'segment': segment,
        'incident_form': IncidentReportForm(),
        'customer': request.user.customer,
    }
    return render(request, 'travel/segment_detail.html', context)

@login_required
def operations_dashboard(request):
    """Dashboard para operadores (requiere permisos especiales)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('home')
    
    today = date.today()
    
    # Arribos de hoy
    arrivals_today = TripSegment.objects.filter(
        scheduled_datetime__date=today,
        service__service_type='flight'
    ).select_related('trip__customer__user', 'service')
    
    # Servicios en curso
    in_progress = TripSegment.objects.filter(
        scheduled_datetime__date=today,
        status='en_route'
    ).select_related('trip__customer__user', 'service')
    
    # Incidencias activas
    active_incidents = Incident.objects.filter(
        resolved_at__isnull=True,
        segment__scheduled_datetime__date=today
    ).select_related('segment__trip__customer__user', 'segment__service')
    
    # Métricas del día
    total_arrivals = TripSegment.objects.filter(
        scheduled_datetime__date=today,
        service__service_type='flight'
    ).count()
    
    confirmed_arrivals = arrivals_today.filter(status='confirmed').count()
    pending_arrivals = arrivals_today.filter(status='pending').count()
    incidents_count = active_incidents.count()
    
    context = {
        'arrivals_today': arrivals_today,
        'in_progress': in_progress,
        'active_incidents': active_incidents,
        'today': today,
        'metrics': {
            'total_arrivals': total_arrivals,
            'confirmed_arrivals': confirmed_arrivals,
            'pending_arrivals': pending_arrivals,
            'incidents_count': incidents_count,
        }
    }
    return render(request, 'travel/operations.html', context)

@csrf_exempt
@login_required
def report_incident(request, segment_id):
    """Reportar incidencia para un segmento"""
    customer = get_object_or_404(Customer, user=request.user)
    segment = get_object_or_404(TripSegment, id=segment_id, trip__customer=customer)
    
    if request.method == 'POST':
        form = IncidentReportForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.segment = segment
            incident.save()
            
            # Crear notificación para el cliente
            Notification.objects.create(
                customer=customer,
                title="Incidencia reportada",
                message=f"Hemos recibido tu reporte: '{incident.title}'. Código de seguimiento: #{incident.id}"
            )
            
            messages.success(request, f'Incidencia reportada correctamente. Código de seguimiento: #{incident.id}')
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': True, 'incident_id': incident.id})
            else:
                return redirect('segment_detail', segment_id=segment_id)
        else:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@csrf_exempt
@login_required
def update_segment_status(request, segment_id):
    """Actualizar estado de un segmento (solo staff)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    if request.method == 'POST':
        segment = get_object_or_404(TripSegment, id=segment_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(TripSegment._meta.get_field('status').choices):
            segment.status = new_status
            if new_status == 'completed':
                segment.actual_datetime = timezone.now()
            segment.save()
            
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def incident_list(request):
    """Lista de incidencias del usuario"""
    customer = get_object_or_404(Customer, user=request.user)
    
    # Filtrar incidencias del cliente
    incidents = Incident.objects.filter(
        segment__trip__customer=customer
    ).select_related('segment__service', 'assigned_to')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        incidents = incidents.filter(status=status_filter)
    
    category_filter = request.GET.get('category')
    if category_filter:
        incidents = incidents.filter(category=category_filter)
    
    # Paginación
    paginator = Paginator(incidents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Incident.STATUS_CHOICES,
        'category_choices': Incident.CATEGORY_CHOICES,
        'current_status': status_filter,
        'current_category': category_filter,
    }
    return render(request, 'travel/incident_list.html', context)

@login_required
def incident_detail(request, incident_id):
    """Detalle de una incidencia específica"""
    customer = get_object_or_404(Customer, user=request.user)
    incident = get_object_or_404(
        Incident, 
        id=incident_id, 
        segment__trip__customer=customer
    )
    
    # Formulario de satisfacción si está resuelta y no calificada
    satisfaction_form = None
    if incident.is_resolved and not incident.customer_satisfaction:
        satisfaction_form = CustomerSatisfactionForm(instance=incident)
        
        if request.method == 'POST' and 'satisfaction' in request.POST:
            satisfaction_form = CustomerSatisfactionForm(request.POST, instance=incident)
            if satisfaction_form.is_valid():
                satisfaction_form.save()
                messages.success(request, 'Gracias por tu calificación')
                return redirect('incident_detail', incident_id=incident_id)
    
    context = {
        'incident': incident,
        'satisfaction_form': satisfaction_form,
    }
    return render(request, 'travel/incident_detail.html', context)

@login_required
def staff_incidents_dashboard(request):
    """Dashboard de incidencias para staff"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('home')
    
    # Estadísticas generales
    today = timezone.now().date()
    
    stats = {
        'total_open': Incident.objects.filter(status='open').count(),
        'total_in_progress': Incident.objects.filter(status='in_progress').count(),
        'overdue': Incident.objects.filter(
            status__in=['open', 'in_progress']
        ).count(),  # Simplificado - implementar is_overdue en queryset después
        'resolved_today': Incident.objects.filter(
            resolved_at__date=today
        ).count(),
        'avg_satisfaction': Incident.objects.filter(
            customer_satisfaction__isnull=False
        ).aggregate(
            avg=models.Avg('customer_satisfaction')
        )['avg'] or 0
    }
    
    # Incidencias por categoría (últimos 7 días)
    week_ago = today - timedelta(days=7)
    category_stats = Incident.objects.filter(
        reported_at__date__gte=week_ago
    ).values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Incidencias recientes
    recent_incidents = Incident.objects.filter(
        status__in=['open', 'in_progress']
    ).select_related(
        'segment__trip__customer__user', 'segment__service', 'assigned_to'
    ).order_by('-reported_at')[:10]
    
    context = {
        'stats': stats,
        'category_stats': category_stats,
        'recent_incidents': recent_incidents,
    }
    return render(request, 'travel/staff_incidents_dashboard.html', context)

@login_required
def staff_incident_detail(request, incident_id):
    """Detalle y resolución de incidencia para staff"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos')
        return redirect('home')
    
    incident = get_object_or_404(Incident, id=incident_id)
    
    if request.method == 'POST':
        form = IncidentResolutionForm(request.POST, instance=incident)
        if form.is_valid():
            incident = form.save(commit=False)
            
            # Si se marca como resuelto, establecer fecha
            if incident.status in ['resolved', 'closed'] and not incident.resolved_at:
                incident.resolved_at = timezone.now()
            
            incident.save()
            
            # Notificar al cliente
            Notification.objects.create(
                customer=incident.segment.trip.customer,
                title=f"Actualización de incidencia #{incident.id}",
                message=f"Tu incidencia '{incident.title}' ha sido actualizada: {incident.get_status_display()}"
            )
            
            messages.success(request, 'Incidencia actualizada correctamente')
            return redirect('staff_incident_detail', incident_id=incident_id)
    else:
        form = IncidentResolutionForm(instance=incident)
    
    context = {
        'incident': incident,
        'form': form,
    }
    return render(request, 'travel/staff_incident_detail.html', context)

@csrf_exempt
@login_required
def get_directions_api(request, segment_id):
    """API mejorada para obtener direcciones con Google Maps"""
    customer = get_object_or_404(Customer, user=request.user)
    segment = get_object_or_404(TripSegment, id=segment_id, trip__customer=customer)
    
    # Obtener ubicación actual del usuario (si se proporciona)
    current_location = request.GET.get('current_location')  # "lat,lng"
    destination = segment.pickup_location or segment.service.location
    
    if not destination:
        return JsonResponse({
            'success': False, 
            'error': 'No hay ubicación de destino definida'
        })
    
    # Usar ubicación actual o ubicación por defecto
    origin = current_location or f"{settings.DEFAULT_LOCATION['lat']},{settings.DEFAULT_LOCATION['lng']}"
    
    # Obtener direcciones
    directions = maps_service.get_directions(origin, destination)
    
    if directions:
        # Agregar información adicional
        directions.update({
            'segment_info': {
                'service_name': segment.service.name,
                'scheduled_time': segment.scheduled_datetime.strftime('%H:%M'),
                'voucher_code': segment.voucher_code
            },
            'destination_info': {
                'name': segment.service.name,
                'address': destination,
                'coordinates': maps_service.geocode_address(destination)
            }
        })
        
        return JsonResponse({
            'success': True,
            'directions': directions
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'No se pudieron obtener las direcciones'
        })

@csrf_exempt
@login_required
def send_whatsapp_reminder(request, segment_id):
    """Enviar recordatorio por WhatsApp"""
    customer = get_object_or_404(Customer, user=request.user)
    segment = get_object_or_404(TripSegment, id=segment_id, trip__customer=customer)
    
    if not customer.phone:
        return JsonResponse({
            'success': False,
            'error': 'No hay número de teléfono registrado'
        })
    
    # Preparar variables para el template
    variables = {
        'name': customer.user.first_name,
        'service_name': segment.service.name,
        'datetime': segment.scheduled_datetime.strftime('%d/%m/%Y %H:%M'),
        'location': segment.pickup_location or 'Por confirmar',
        'voucher_code': segment.voucher_code
    }
    
    # Enviar mensaje
    result = whatsapp_service.send_template_message(
        customer.phone, 
        'itinerary_reminder', 
        variables
    )
    
    if result['success']:
        # Crear notificación
        Notification.objects.create(
            customer=customer,
            title="Recordatorio enviado por WhatsApp",
            message=f"Se envió recordatorio de {segment.service.name} a tu WhatsApp"
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Recordatorio enviado por WhatsApp'
        })
    else:
        return JsonResponse({
            'success': False,
            'error': result['error']
        })

@login_required
def nearby_recommendations(request):
    """Obtener recomendaciones de lugares cercanos"""
    lat = request.GET.get('lat', settings.DEFAULT_LOCATION['lat'])
    lng = request.GET.get('lng', settings.DEFAULT_LOCATION['lng'])
    place_type = request.GET.get('type', 'restaurant')  # restaurant, tourist_attraction, etc.
    
    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        lat = settings.DEFAULT_LOCATION['lat']
        lng = settings.DEFAULT_LOCATION['lng']
    
    # Obtener lugares cercanos
    places = maps_service.find_nearby_places(lat, lng, place_type)
    
    return JsonResponse({
        'success': True,
        'places': places,
        'location': {'lat': lat, 'lng': lng}
    })

@csrf_exempt
@login_required  
def emergency_whatsapp_contact(request):
    """Contacto de emergencia vía WhatsApp"""
    if request.method == 'POST':
        customer = get_object_or_404(Customer, user=request.user)
        
        if not customer.phone:
            return JsonResponse({
                'success': False,
                'error': 'No hay número de WhatsApp registrado'
            })
        
        # Obtener información adicional del request
        data = json.loads(request.body) if request.body else {}
        emergency_type = data.get('type', 'general')
        location = data.get('location', 'No especificada')
        details = data.get('details', '')
        
        # Preparar variables para el template
        variables = {
            'name': customer.user.first_name,
            'emergency_type': emergency_type,
            'location': location,
            'details': details
        }
        
        # Enviar mensaje de emergencia
        result = whatsapp_service.send_template_message(
            customer.phone,
            'emergency_contact',
            variables
        )
        
        # También notificar al equipo de emergencias
        emergency_message = f"""
🚨 EMERGENCIA REPORTADA

Cliente: {customer.user.get_full_name()}
Teléfono: {customer.phone}
Tipo: {emergency_type}
Ubicación: {location}
Detalles: {details}

Contactar inmediatamente.
        """
        
        # Enviar a número de emergencias del equipo
        whatsapp_service.send_message('+56999990000', emergency_message)
        
        # Crear notificación
        Notification.objects.create(
            customer=customer,
            title="Contacto de emergencia activado",
            message="Hemos recibido tu solicitud de emergencia. Te contactaremos inmediatamente."
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Emergencia reportada. Te contactaremos en 5 minutos.'
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def recommendations_view(request):
    """Vista de recomendaciones de lugares"""
    customer = get_object_or_404(Customer, user=request.user)
    
    context = {
        'customer': customer,
        'default_location': {
            'lat': settings.DEFAULT_LOCATION.get('lat', -41.2985),
            'lng': settings.DEFAULT_LOCATION.get('lng', -72.9781),
            'city': settings.DEFAULT_LOCATION.get('city', 'Puerto Varas')
        }
    }
    return render(request, 'travel/recommendations.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')  