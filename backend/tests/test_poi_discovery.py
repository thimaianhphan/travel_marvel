import sys
import os
import logging

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services.poi_discovery.poi_discovery_service import discover_pois_along_route

# Configure logging to see the debug output
logging.basicConfig(level=logging.INFO)

def test_poi_discovery():
    # Test coordinates (example: Munich to Neuschwanstein Castle)
    start_lat, start_lon = 48.1351, 11.5820  # Munich
    end_lat, end_lon = 47.5576, 10.7498      # Neuschwanstein

    # Try to discover POIs
    pois = discover_pois_along_route(
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon,
        search_radius_km=30,
        max_pois=3,
        prioritize_scenic=True
    )

    # Print results
    print("\nDiscovered POIs:")
    print("-" * 50)
    for i, poi in enumerate(pois, 1):
        print(f"{i}. {poi.name}")
        print(f"   Location: {poi.lat}, {poi.lon}")
        print(f"   Type: {poi.poi_type}")
        print(f"   Score: {poi.score}")
        print(f"   Position along route: {poi.position_along_route:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    test_poi_discovery()