# travel/admin.py
from django.contrib import admin
from .models import Customer, Trip, Service, TripSegment, Incident, Notification
from django.utils import timezone

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['customer', 'destination', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'start_date', 'destination']
    search_fields = ['customer__user__first_name', 'customer__user__last_name', 'destination']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'location']
    list_filter = ['service_type']
    search_fields = ['name', 'location']

@admin.register(TripSegment)
class TripSegmentAdmin(admin.ModelAdmin):
    list_display = ['trip', 'service', 'scheduled_datetime', 'status', 'voucher_code']
    list_filter = ['status', 'service__service_type', 'scheduled_datetime']
    search_fields = ['trip__customer__user__first_name', 'service__name', 'voucher_code']
    date_hierarchy = 'scheduled_datetime'

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'segment', 'category', 'severity', 'status', 'reported_at', 'assigned_to', 'is_resolved']
    list_filter = ['status', 'severity', 'category', 'reported_at', 'assigned_to']
    search_fields = ['title', 'description', 'segment__trip__customer__user__first_name', 
                    'segment__trip__customer__user__last_name']
    readonly_fields = ['reported_at', 'response_time']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('segment', 'title', 'description', 'category')
        }),
        ('Clasificación', {
            'fields': ('severity', 'status', 'assigned_to')
        }),
        ('Detalles del incidente', {
            'fields': ('location', 'incident_datetime', 'affected_passengers', 'reporter_contact')
        }),
        ('Resolución', {
            'fields': ('resolution_notes', 'internal_notes', 'requires_followup')
        }),
        ('Seguimiento', {
            'fields': ('reported_at', 'resolved_at', 'customer_satisfaction', 'evidence_description'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_resolved', 'assign_to_me', 'escalate_severity']
    
    def mark_resolved(self, request, queryset):
        count = queryset.filter(status__in=['open', 'in_progress']).update(
            status='resolved',
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{count} incidencias marcadas como resueltas')
    mark_resolved.short_description = 'Marcar como resueltas'
    
    def assign_to_me(self, request, queryset):
        count = queryset.update(assigned_to=request.user)
        self.message_user(request, f'{count} incidencias asignadas a ti')
    assign_to_me.short_description = 'Asignar a mí'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['customer', 'title', 'read', 'created_at']
    list_filter = ['read', 'created_at']
