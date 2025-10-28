# travel/services/google_maps.py
import googlemaps
import requests
from django.conf import settings
from typing import Dict, List, Optional, Tuple

class GoogleMapsService:
    """Servicio para integración con Google Maps API"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        if self.api_key:
            self.client = googlemaps.Client(key=self.api_key)
        else:
            self.client = None
    
    def is_available(self) -> bool:
        """Verificar si el servicio está disponible"""
        return self.client is not None
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Obtener coordenadas de una dirección"""
        if not self.is_available():
            return None
        
        try:
            geocode_result = self.client.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': geocode_result[0]['formatted_address'],
                    'place_id': geocode_result[0]['place_id']
                }
        except Exception as e:
            print(f"Error en geocoding: {e}")
            return None
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """Obtener dirección de coordenadas"""
        if not self.is_available():
            return None
        
        try:
            reverse_geocode_result = self.client.reverse_geocode((lat, lng))
            if reverse_geocode_result:
                return {
                    'formatted_address': reverse_geocode_result[0]['formatted_address'],
                    'place_id': reverse_geocode_result[0]['place_id']
                }
        except Exception as e:
            print(f"Error en reverse geocoding: {e}")
            return None
    
    def get_directions(self, origin: str, destination: str, mode: str = 'driving') -> Optional[Dict]:
        """Obtener direcciones entre dos puntos"""
        if not self.is_available():
            return self._get_mock_directions(origin, destination)
        
        try:
            directions_result = self.client.directions(
                origin,
                destination,
                mode=mode,
                language='es'
            )
            
            if directions_result:
                route = directions_result[0]
                leg = route['legs'][0]
                
                return {
                    'duration': leg['duration']['text'],
                    'duration_value': leg['duration']['value'],  # en segundos
                    'distance': leg['distance']['text'],
                    'distance_value': leg['distance']['value'],  # en metros
                    'start_address': leg['start_address'],
                    'end_address': leg['end_address'],
                    'steps': [
                        {
                            'instruction': step['html_instructions'],
                            'distance': step['distance']['text'],
                            'duration': step['duration']['text']
                        } for step in leg['steps']
                    ],
                    'polyline': route['overview_polyline']['points']
                }
        except Exception as e:
            print(f"Error obteniendo direcciones: {e}")
            return self._get_mock_directions(origin, destination)
    
    def _get_mock_directions(self, origin: str, destination: str) -> Dict:
        """Direcciones mock cuando no hay API disponible"""
        return {
            'duration': '15 min',
            'duration_value': 900,
            'distance': '2.5 km',
            'distance_value': 2500,
            'start_address': origin,
            'end_address': destination,
            'steps': [
                {
                    'instruction': f'Dirigirse hacia {destination}',
                    'distance': '2.5 km',
                    'duration': '15 min'
                }
            ],
            'polyline': ''
        }
    
    def find_nearby_places(self, lat: float, lng: float, place_type: str = 'restaurant', radius: int = 1500) -> List[Dict]:
        """Buscar lugares cercanos"""
        if not self.is_available():
            return self._get_mock_places(place_type)
        
        try:
            places_result = self.client.places_nearby(
                location=(lat, lng),
                radius=radius,
                type=place_type,
                language='es'
            )
            
            places = []
            for place in places_result['results'][:10]:  # Máximo 10 resultados
                places.append({
                    'name': place['name'],
                    'rating': place.get('rating', 0),
                    'price_level': place.get('price_level', 0),
                    'vicinity': place['vicinity'],
                    'place_id': place['place_id'],
                    'types': place['types'],
                    'photo_reference': place.get('photos', [{}])[0].get('photo_reference') if place.get('photos') else None
                })
            
            return places
        except Exception as e:
            print(f"Error buscando lugares: {e}")
            return self._get_mock_places(place_type)
    
    def _get_mock_places(self, place_type: str) -> List[Dict]:
        """Lugares mock para desarrollo"""
        mock_places = {
            'restaurant': [
                {'name': 'Restaurant Casa Valdés', 'rating': 4.5, 'vicinity': 'Centro Puerto Varas'},
                {'name': 'Mesa Tropera', 'rating': 4.3, 'vicinity': 'Av. Costanera'},
                {'name': 'Café Mawen', 'rating': 4.6, 'vicinity': 'Centro'}
            ],
            'tourist_attraction': [
                {'name': 'Iglesia del Sagrado Corazón', 'rating': 4.4, 'vicinity': 'Centro'},
                {'name': 'Costanera Puerto Varas', 'rating': 4.7, 'vicinity': 'Costanera'},
                {'name': 'Casa Kuschel', 'rating': 4.2, 'vicinity': 'Centro histórico'}
            ]
        }
        return mock_places.get(place_type, [])

    def get_static_map_url(self, lat: float, lng: float, zoom: int = 15, size: str = "600x400") -> str:
        """Generar URL de mapa estático"""
        if not self.is_available():
            return f"https://via.placeholder.com/{size}/0066cc/ffffff?text=Mapa+no+disponible"
        
        return (f"https://maps.googleapis.com/maps/api/staticmap?"
                f"center={lat},{lng}&zoom={zoom}&size={size}&maptype=roadmap"
                f"&markers=color:red|{lat},{lng}&key={self.api_key}")
