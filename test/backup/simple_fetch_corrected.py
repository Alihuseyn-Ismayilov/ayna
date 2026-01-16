import requests
import json
import math
import csv

def google_coords_to_latlon(world_x, world_y):
    """Convert Google Maps coordinates using zoom level 23"""
    map_size = 256 * (2 ** 23)  # 2,147,483,648
    x = world_x / map_size
    y = world_y / map_size
    lon = x * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))
    return lat, lon

# Your API request code
headers = {
    'accept': '*/*',
    'origin': 'https://map.ayna.gov.az',
    'referer': 'https://map.ayna.gov.az/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

response = requests.get(
    'https://mapsresources-pa.googleapis.com/v1/featureMaps?map_id=47b57ca3c234946a&version=17854301209442801430&pb=!1m4!1m3!1i12!2i2613!3i1543!1m4!1m3!1i12!2i2614!3i1543!1m4!1m3!1i12!2i2615!3i1543!1m4!1m3!1i12!2i2613!3i1544!1m4!1m3!1i12!2i2613!3i1545!1m4!1m3!1i12!2i2614!3i1544!1m4!1m3!1i12!2i2614!3i1545!1m4!1m3!1i12!2i2615!3i1544!1m4!1m3!1i12!2i2615!3i1545!1m4!1m3!1i12!2i2616!3i1543!1m4!1m3!1i12!2i2617!3i1543!1m4!1m3!1i12!2i2616!3i1544!1m4!1m3!1i12!2i2616!3i1545!1m4!1m3!1i12!2i2617!3i1544!1m4!1m3!1i12!2i2617!3i1545!2m3!1e0!2sm!3i762526034!3m13!2str-TR!3sUS!5e18!12m5!1e68!2m2!1sset!2sRoadmap!4e2!12m3!1e37!2m1!1ssmartmaps!4e3!12m1!5b1!23i46991212!23i47054750!23i47083502!23i56565656!26m2!1e2!1e3',
    headers=headers
)

maps_data = response.json()
locations = []

for tile in maps_data:
    base = tile.get('base', [None, None])
    if not base[0]: continue
    
    for feature in tile.get('features', []):
        try:
            title = json.loads(feature.get('c', '{}')).get('1', {}).get('title', 'Unknown')
        except:
            title = 'Unknown'
        
        coords = feature.get('a', [])
        world_x = base[0] + (coords[0] if len(coords) > 0 else 0)
        world_y = base[1] + (coords[1] if len(coords) > 1 else 0)
        
        lat, lon = google_coords_to_latlon(world_x, world_y)
        
        if 40.0 <= lat <= 41.0 and 49.0 <= lon <= 51.0:  # Baku bounds
            locations.append({'title': title, 'lat': lat, 'lon': lon})

# Save to CSV
with open('baku_locations.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'lat', 'lon'])
    writer.writeheader()
    writer.writerows(locations)

print(f"✅ Saved {len(locations)} locations")
for loc in locations[:5]:
    print(f"   {loc['title']}: {loc['lat']:.5f}, {loc['lon']:.5f}")
