# travel/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
        # Preferencias de comunicación
    whatsapp_notifications = models.BooleanField(default=True, help_text="Recibir notificaciones por WhatsApp")
    whatsapp_reminders = models.BooleanField(default=True, help_text="Recibir recordatorios por WhatsApp")
    
    def send_whatsapp(self, template_name: str, variables: dict):
        """Enviar mensaje de WhatsApp si está habilitado"""
        if self.whatsapp_notifications and self.phone:
            return whatsapp_service.send_template_message(
                self.phone, template_name, variables
            )
        return {'success': False, 'error': 'WhatsApp not enabled'}

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class Trip(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='trips')
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    total_passengers = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=[
        ('confirmed', 'Confirmado'),
        ('pending', 'Pendiente'),
        ('cancelled', 'Cancelado'),
        ('completed', 'Completado'),
    ], default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.customer} - {self.destination} ({self.start_date})"

class Service(models.Model):
    SERVICE_TYPES = [
        ('flight', 'Vuelo'),
        ('transfer', 'Traslado'),
        ('hotel', 'Hotel'),
        ('tour', 'Tour'),
        ('activity', 'Actividad'),
    ]

    name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    includes = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)

    def __str__(self):
        return self.name

class TripSegment(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='segments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    scheduled_datetime = models.DateTimeField()
    actual_datetime = models.DateTimeField(null=True, blank=True)
    pickup_location = models.CharField(max_length=200, blank=True)
    destination_location = models.CharField(max_length=200, blank=True)
    provider = models.CharField(max_length=100, blank=True)
    provider_contact = models.CharField(max_length=100, blank=True)
    voucher_code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('confirmed', 'Confirmado'),
        ('pending', 'Pendiente'),
        ('en_route', 'En camino'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ], default='confirmed')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
        # Coordenadas de ubicación
    pickup_latitude = models.FloatField(null=True, blank=True, help_text="Latitud punto de encuentro")
    pickup_longitude = models.FloatField(null=True, blank=True, help_text="Longitud punto de encuentro")
    destination_latitude = models.FloatField(null=True, blank=True, help_text="Latitud destino")
    destination_longitude = models.FloatField(null=True, blank=True, help_text="Longitud destino")
    
    # Información de direcciones
    directions_duration = models.CharField(max_length=50, blank=True, help_text="Duración estimada")
    directions_distance = models.CharField(max_length=50, blank=True, help_text="Distancia estimada")
    last_directions_update = models.DateTimeField(null=True, blank=True)
    
    @property
    def has_coordinates(self):
        return (self.pickup_latitude is not None and 
                self.pickup_longitude is not None)
    
    def update_coordinates(self):
        """Actualizar coordenadas usando Google Maps"""
        if self.pickup_location:
            coords = maps_service.geocode_address(self.pickup_location)
            if coords:
                self.pickup_latitude = coords['lat']
                self.pickup_longitude = coords['lng']
                self.save(update_fields=['pickup_latitude', 'pickup_longitude'])

    class Meta:
        ordering = ['scheduled_datetime']

    def __str__(self):
        return f"{self.trip.customer} - {self.service.name} ({self.scheduled_datetime.date()})"

class Incident(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Abierta'),
        ('in_progress', 'En Progreso'),
        ('resolved', 'Resuelta'),
        ('closed', 'Cerrada'),
    ]
    
    CATEGORY_CHOICES = [
        ('transport', 'Transporte'),
        ('accommodation', 'Alojamiento'),
        ('service_quality', 'Calidad de Servicio'),
        ('schedule', 'Horarios'),
        ('safety', 'Seguridad'),
        ('weather', 'Clima'),
        ('health', 'Salud'),
        ('documentation', 'Documentación'),
        ('communication', 'Comunicación'),
        ('other', 'Otros'),
    ]

    # Información básica
    segment = models.ForeignKey('TripSegment', on_delete=models.CASCADE, related_name='incidents')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    
    # Ubicación y contexto
    location = models.CharField(max_length=200, blank=True, help_text="Ubicación donde ocurrió el incidente")
    incident_datetime = models.DateTimeField(default=timezone.now, help_text="Cuándo ocurrió el incidente")
    
    # Personas involucradas
    affected_passengers = models.IntegerField(default=1, help_text="Número de pasajeros afectados")
    reporter_contact = models.CharField(max_length=100, blank=True, help_text="Teléfono del reportero")
    
    # Seguimiento
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_incidents', help_text="Staff asignado")
    
    # Campos adicionales
    requires_followup = models.BooleanField(default=False, help_text="Requiere seguimiento adicional")
    customer_satisfaction = models.IntegerField(null=True, blank=True, 
                                              help_text="Calificación del cliente (1-5)")
    internal_notes = models.TextField(blank=True, help_text="Notas internas del equipo")
    
    # Archivos adjuntos (para futuro)
    evidence_description = models.TextField(blank=True, help_text="Descripción de evidencias (fotos, videos)")
    
    class Meta:
        ordering = ['-reported_at']
        
    @property
    def is_resolved(self):
        return self.status in ['resolved', 'closed']
    
    @property
    def response_time(self):
        """Tiempo de respuesta en horas"""
        if self.resolved_at:
            diff = self.resolved_at - self.reported_at
            return round(diff.total_seconds() / 3600, 2)
        else:
            diff = timezone.now() - self.reported_at
            return round(diff.total_seconds() / 3600, 2)
    
    @property
    def is_overdue(self):
        """Verificar si está vencida (más de 24h sin resolver para alta/crítica)"""
        if self.is_resolved:
            return False
        
        hours_passed = self.response_time
        
        if self.severity == 'critical':
            return hours_passed > 4  # 4 horas para crítica
        elif self.severity == 'high':
            return hours_passed > 12  # 12 horas para alta
        elif self.severity == 'medium':
            return hours_passed > 24  # 24 horas para media
        else:
            return hours_passed > 48  # 48 horas para baja

    def __str__(self):
        return f"{self.title} - {self.segment.trip.customer.user.get_full_name()}"

class Notification(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer} - {self.title}"