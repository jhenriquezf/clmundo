# travel/urls.py (actualizado)
from django.urls import path
from . import views, api
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Páginas principales
    path('', views.landing_page, name='landing'),
    path('magic-link/', views.magic_link_login, name='magic_link_login'),
    path('home/', views.home, name='home'),
    path('segment/<int:segment_id>/', views.segment_detail, name='segment_detail'),
    path('operations/', views.operations_dashboard, name='operations'),
    path('notifications/', views.notifications_list, name='notifications'),
        # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # API endpoints
    path('api/incident/<int:segment_id>/', views.report_incident, name='report_incident'),
    path('api/segment/<int:segment_id>/status/', views.update_segment_status, name='update_segment_status'),
    path('api/segment/<int:segment_id>/status-info/', api.get_segment_status, name='get_segment_status'),
    path('api/voucher/<int:segment_id>/download/', views.download_voucher, name='download_voucher'),
    path('api/directions/<int:segment_id>/', views.get_directions, name='get_directions'),
    path('api/emergency/', api.emergency_contact, name='emergency_contact'),
    # Incidencias - Cliente
    path('api/incident/<int:segment_id>/', views.report_incident, name='report_incident'),
    path('my-incidents/', views.incident_list, name='incident_list'),
    path('incident/<int:incident_id>/', views.incident_detail, name='incident_detail'),
    
    # Incidencias - Staff
    path('staff/incidents/', views.staff_incidents_dashboard, name='staff_incidents_dashboard'),
    path('staff/incident/<int:incident_id>/', views.staff_incident_detail, name='staff_incident_detail'),
    
    # Incidencias
    path('my-incidents/', views.incident_list, name='incident_list'),
    path('incident/<int:incident_id>/', views.incident_detail, name='incident_detail'),
    
    # APIs externas - NUEVAS RUTAS
    path('api/directions/<int:segment_id>/', views.get_directions_api, name='get_directions_api'),
    path('api/nearby-places/', views.nearby_recommendations, name='nearby_recommendations'),
    path('api/whatsapp-reminder/<int:segment_id>/', views.send_whatsapp_reminder, name='send_whatsapp_reminder'),
    path('api/emergency/', views.emergency_whatsapp_contact, name='emergency_whatsapp_contact'),
    path('api/incident/<int:segment_id>/', views.report_incident, name='report_incident'),
    path('api/voucher/<int:segment_id>/download/', views.download_voucher, name='download_voucher'),
    
    # Nueva vista de recomendaciones
    path('recommendations/', views.recommendations_view, name='recommendations'),
]