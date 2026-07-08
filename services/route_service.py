from routing.safe_route import find_safe_route
import logging

logging.basicConfig(level=logging.INFO)

def get_safe_route(start_lat, start_lon, end_lat, end_lon):
    """
    Get safe route between two points
    Returns route with AQI information
    """
    try:
        route_data = find_safe_route(
            (start_lat, start_lon),
            (end_lat, end_lon)
        )
        return route_data
    except Exception as e:
        logging.error(f"Route service error: {e}")
        return {
            'error': str(e),
            'route': None,
            'message': 'Could not calculate safe route'
        }