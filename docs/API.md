# docs/API.md
# API Documentation - ClMundo

## Endpoints Principales

### Autenticación
- `POST /magic-link/` - Login con magic link
- `POST /api/emergency/` - Contacto de emergencia

### Segmentos de viaje
- `GET /segment/{id}/` - Detalle de segmento
- `POST /api/segment/{id}/status/` - Actualizar estado (staff only)
- `GET /api/segment/{id}/status-info/` - Información de estado
- `GET /api/directions/{id}/` - Direcciones al punto de encuentro

### Incidencias
- `POST /api/incident/{segment_id}/` - Reportar incidencia

### Vouchers
- `GET /api/voucher/{segment_id}/download/` - Descargar voucher

## Modelos de Datos

### Customer
- user: OneToOne con User de Django
- phone: Teléfono de contacto
- emergency_contact: Contacto de emergencia
- preferences: JSON con preferencias del usuario

### Trip
- customer: Cliente del viaje
- destination: Destino del viaje
- start_date/end_date: Fechas del viaje
- total_passengers: Número de pasajeros
- status: Estado del viaje

### TripSegment
- trip: Viaje al que pertenece
- service: Servicio contratado
- scheduled_datetime: Fecha/hora programada
- pickup_location: Punto de encuentro
- status: Estado actual
- voucher_code: Código único del voucher

### Incident
- segment: Segmento afectado
- title: Título de la incidencia
- description: Descripción detallada
- severity: Nivel de severidad
- resolved_at: Fecha de resolución