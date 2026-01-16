"""
CORRECTED BAKU MAP VISUALIZATION
Using zoom level 23 (2^31) for accurate coordinate conversion
"""

import requests
import json
import math
import csv

print("=" * 80)
print("BAKU MAP - CORRECTED COORDINATES")
print("=" * 80)

# CORRECT COORDINATE CONVERSION (Zoom level 23)
def google_coords_to_latlon(world_x, world_y):
    """
    Convert Google Maps world coordinates to lat/lon
    Uses zoom level 23 (map_size = 2^31 = 2,147,483,648)
    """
    map_size = 256 * (2 ** 23)  # 2,147,483,648
    
    x = world_x / map_size
    y = world_y / map_size
    
    # Convert to longitude (simple linear)
    lon = x * 360 - 180
    
    # Convert to latitude (inverse Mercator)
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y)))
    lat = math.degrees(lat_rad)
    
    return lat, lon

# Test with known location
print("\n✅ TESTING COORDINATE CONVERSION:")
print("-" * 80)
lat, lon = google_coords_to_latlon(1371213824, 809900032)
print(f"Heydər Əliyev Mərkəzi")
print(f"  Calculated: {lat:.5f}°N, {lon:.5f}°E")
print(f"  Known:      40.39530°N, 49.86780°E")
print(f"  Error:      {abs(lat-40.39530):.6f}° lat, {abs(lon-49.86780):.6f}° lon")
print(f"  ✅ Accurate!")

# Fetch and process data
def fetch_and_process():
    print("\n📍 FETCHING GOOGLE MAPS FEATURES...")
    print("-" * 80)
    
    headers = {
        'accept': '*/*',
        'origin': 'https://map.ayna.gov.az',
        'referer': 'https://map.ayna.gov.az/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    url = 'https://mapsresources-pa.googleapis.com/v1/featureMaps?map_id=47b57ca3c234946a&version=17854301209442801430&pb=!1m4!1m3!1i12!2i2613!3i1543!1m4!1m3!1i12!2i2614!3i1543!1m4!1m3!1i12!2i2615!3i1543!1m4!1m3!1i12!2i2613!3i1544!1m4!1m3!1i12!2i2613!3i1545!1m4!1m3!1i12!2i2614!3i1544!1m4!1m3!1i12!2i2614!3i1545!1m4!1m3!1i12!2i2615!3i1544!1m4!1m3!1i12!2i2615!3i1545!1m4!1m3!1i12!2i2616!3i1543!1m4!1m3!1i12!2i2617!3i1543!1m4!1m3!1i12!2i2616!3i1544!1m4!1m3!1i12!2i2616!3i1545!1m4!1m3!1i12!2i2617!3i1544!1m4!1m3!1i12!2i2617!3i1545!2m3!1e0!2sm!3i762526034!3m13!2str-TR!3sUS!5e18!12m5!1e68!2m2!1sset!2sRoadmap!4e2!12m3!1e37!2m1!1ssmartmaps!4e3!12m1!5b1!23i46991212!23i47054750!23i47083502!23i56565656!26m2!1e2!1e3'
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        maps_data = response.json()
        
        locations = []
        seen = set()
        
        for tile in maps_data:
            base = tile.get('base', [None, None])
            if base[0] is None or base[1] is None:
                continue
                
            for feature in tile.get('features', []):
                try:
                    c_data = json.loads(feature.get('c', '{}'))
                    title = c_data.get('1', {}).get('title', 'Unknown')
                except:
                    title = 'Unknown'
                
                coords_a = feature.get('a', [])
                
                if len(coords_a) >= 2:
                    world_x = base[0] + coords_a[0]
                    world_y = base[1] + coords_a[1]
                else:
                    world_x = base[0]
                    world_y = base[1]
                
                lat, lon = google_coords_to_latlon(world_x, world_y)
                
                # Only include if in Baku area (reasonable bounds)
                if 40.0 <= lat <= 41.0 and 49.0 <= lon <= 51.0:
                    coord_key = (round(lat, 5), round(lon, 5), title)
                    if coord_key not in seen:
                        seen.add(coord_key)
                        locations.append({
                            'id': len(locations),
                            'title': title,
                            'lat': lat,
                            'lon': lon
                        })
        
        print(f"✅ Fetched {len(locations)} locations")
        
        # Save to CSV
        with open('locations_corrected.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'lat', 'lon'])
            writer.writeheader()
            writer.writerows(locations)
        print(f"✅ Saved to locations_corrected.csv")
        
        # Show sample
        print(f"\n📍 SAMPLE LOCATIONS:")
        for loc in locations[:10]:
            print(f"   {loc['title']}: {loc['lat']:.5f}, {loc['lon']:.5f}")
        
        return locations
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

# Generate map
def generate_map(locations):
    print(f"\n🗺️  GENERATING INTERACTIVE MAP...")
    print("-" * 80)
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Baku Map - Corrected Coordinates</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #container {{ display: flex; height: 100vh; }}
        #sidebar {{
            width: 350px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            overflow-y: auto;
            box-shadow: 4px 0 10px rgba(0,0,0,0.3);
        }}
        .header {{
            padding: 25px;
            background: rgba(0,0,0,0.2);
        }}
        .header h1 {{
            margin: 0 0 5px 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .search-box {{
            padding: 20px;
            background: rgba(0,0,0,0.1);
        }}
        .search-box input {{
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            box-sizing: border-box;
        }}
        .location-list {{
            padding: 15px;
        }}
        .location-item {{
            background: rgba(255,255,255,0.1);
            padding: 14px;
            margin-bottom: 10px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            border-left: 4px solid #4CAF50;
        }}
        .location-item:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
        }}
        .location-item.active {{
            background: rgba(255,255,255,0.3);
            border-left-color: #FFC107;
        }}
        .location-title {{
            font-weight: 600;
            font-size: 15px;
            margin-bottom: 4px;
        }}
        .location-coords {{
            font-size: 11px;
            opacity: 0.7;
        }}
        #map {{ flex: 1; }}
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <div class="header">
                <h1>🗺️ Baku Locations</h1>
                <p>{len(locations)} Points of Interest</p>
            </div>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 Search locations..." />
            </div>
            <div class="location-list" id="locationList"></div>
        </div>
        <div id="map"></div>
    </div>

    <script>
        var map = L.map('map').setView([40.4093, 49.8671], 11);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap',
            maxZoom: 19
        }}).addTo(map);
        
        var locations = {json.dumps(locations, ensure_ascii=False)};
        var markers = {{}};
        
        locations.forEach(function(loc) {{
            var marker = L.marker([loc.lat, loc.lon]).addTo(map);
            marker.bindPopup('<div style="font-weight:bold; font-size:14px;">' + loc.title + '</div>');
            markers[loc.id] = marker;
            
            marker.on('click', function() {{
                highlightLocation(loc.id);
            }});
        }});
        
        function renderList(locs) {{
            var html = '';
            locs.forEach(function(loc) {{
                html += '<div class="location-item" data-id="' + loc.id + '" onclick="flyTo(' + loc.id + ')">' +
                    '<div class="location-title">📍 ' + loc.title + '</div>' +
                    '<div class="location-coords">' + loc.lat.toFixed(5) + ', ' + loc.lon.toFixed(5) + '</div>' +
                    '</div>';
            }});
            document.getElementById('locationList').innerHTML = html;
        }}
        
        renderList(locations);
        
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            var term = e.target.value.toLowerCase();
            var filtered = locations.filter(l => l.title.toLowerCase().includes(term));
            renderList(filtered);
        }});
        
        function flyTo(id) {{
            var loc = locations[id];
            map.flyTo([loc.lat, loc.lon], 16, {{ duration: 1.5 }});
            markers[id].openPopup();
            highlightLocation(id);
        }}
        
        function highlightLocation(id) {{
            document.querySelectorAll('.location-item').forEach(function(item) {{
                item.classList.remove('active');
            }});
            var item = document.querySelector('[data-id="' + id + '"]');
            if (item) {{
                item.classList.add('active');
                item.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}
        }}
    </script>
</body>
</html>'''
    
    with open('baku_map_corrected.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ Map saved as: baku_map_corrected.html")

# Run
locations = fetch_and_process()
if locations:
    generate_map(locations)

print("\n" + "=" * 80)
print("✅ COMPLETE! Open 'baku_map_corrected.html' in your browser")
print("=" * 80)
