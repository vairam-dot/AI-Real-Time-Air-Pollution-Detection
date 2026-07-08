import networkx as nx
import osmnx as ox
from geopy.distance import distance
import logging

logging.basicConfig(level=logging.INFO)

# Cache for road networks
_graph_cache = {}

def get_road_network(center_lat, center_lon, dist=5000):
    """Get or load road network for area"""
    cache_key = f"{center_lat:.2f}_{center_lon:.2f}"
    
    if cache_key in _graph_cache:
        return _graph_cache[cache_key]
    
    try:
        # Download road network from OpenStreetMap
        G = ox.graph_from_point(
            (center_lat, center_lon),
            dist=dist,
            network_type='drive'
        )
        _graph_cache[cache_key] = G
        logging.info(f"Loaded road network for {cache_key}")
        return G
    except Exception as e:
        logging.error(f"Failed to load road network: {e}")
        return None

def estimate_road_aqi(lat, lon):
    """
    Estimate AQI for a road based on location
    In real app, this would use nearby sensor data
    """
    # Simple simulation - AQI varies by area
    import random
    base = 100
    variation = random.uniform(-20, 20)
    return max(20, min(400, base + variation))

def find_safe_route(start, end, max_distance=10000):
    """
    Find route that avoids high pollution areas
    """
    try:
        # Get road network
        center_lat = (start[0] + end[0]) / 2
        center_lon = (start[1] + end[1]) / 2
        G = get_road_network(center_lat, center_lon)
        
        if G is None:
            return _get_dummy_route(start, end)
        
        # Find nearest nodes
        start_node = ox.distance.nearest_nodes(G, start[1], start[0])
        end_node = ox.distance.nearest_nodes(G, end[1], end[0])
        
        # Calculate shortest path (distance)
        shortest_path = nx.shortest_path(G, start_node, end_node, weight='length')
        shortest_distance = sum(nx.shortest_path_length(G, start_node, end_node, weight='length'))
        
        # Calculate safe path (weighted by AQI)
        for u, v, data in G.edges(data=True):
            # Add AQI weight to edges
            mid_lat = (G.nodes[u]['y'] + G.nodes[v]['y']) / 2
            mid_lon = (G.nodes[u]['x'] + G.nodes[v]['x']) / 2
            aqi = estimate_road_aqi(mid_lat, mid_lon)
            
            # Weight: distance * (1 + aqi/100)
            data['aqi_weight'] = data['length'] * (1 + aqi/100)
        
        # Find path minimizing AQI exposure
        try:
            safe_path = nx.shortest_path(G, start_node, end_node, weight='aqi_weight')
            safe_distance = nx.shortest_path_length(G, start_node, end_node, weight='aqi_weight')
        except:
            # Fallback to shortest path
            safe_path = shortest_path
            safe_distance = shortest_distance
        
        # Convert to coordinates
        shortest_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
        safe_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in safe_path]
        
        # Calculate average AQI for each route
        shortest_aqi = sum(estimate_road_aqi(lat, lon) for lat, lon in shortest_coords) / len(shortest_coords)
        safe_aqi = sum(estimate_road_aqi(lat, lon) for lat, lon in safe_coords) / len(safe_coords)
        
        return {
            'shortest_route': {
                'coordinates': shortest_coords,
                'distance': shortest_distance / 1000,  # km
                'avg_aqi': round(shortest_aqi, 1)
            },
            'safe_route': {
                'coordinates': safe_coords,
                'distance': safe_distance / 1000,  # km
                'avg_aqi': round(safe_aqi, 1)
            },
            'improvement': round(shortest_aqi - safe_aqi, 1)
        }
        
    except Exception as e:
        logging.error(f"Route calculation error: {e}")
        return _get_dummy_route(start, end)

def _get_dummy_route(start, end):
    """Return dummy route for testing"""
    return {
        'shortest_route': {
            'coordinates': [start, end],
            'distance': 5.2,
            'avg_aqi': 156
        },
        'safe_route': {
            'coordinates': [
                start,
                ((start[0] + end[0])/2, (start[1] + end[1])/2),
                end
            ],
            'distance': 6.8,
            'avg_aqi': 98
        },
        'improvement': 58
    }