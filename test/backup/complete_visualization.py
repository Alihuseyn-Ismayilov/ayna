"""
COMPLETE BAKU MAP VISUALIZATION
Combines all 4 data sources into interactive map
"""

import requests
import json
import csv
import sqlite3
import math

print("=" * 80)
print("BAKU INTEGRATED MAP VISUALIZATION")
print("=" * 80)

# =============================================================================
# STEP 1: FETCH ALL DATA
# =============================================================================

def fetch_google_maps_features():
    """Fetch POIs from Google Maps"""
    print("\n📍 Fetching Google Maps features...")
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
        return response.json()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def fetch_bus_data():
    """Fetch bus routes and stops"""
    print("\n🚌 Fetching bus data...")
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://map.ayna.gov.az',
        'Referer': 'https://map.ayna.gov.az/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        response = requests.get('https://map-api.ayna.gov.az/api/bus/getBusList', headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def google_coords_to_latlon(world_x, world_y):
    """Convert Google Maps world coordinates to lat/lon"""
    SCALE = 2 ** 21  
    x = world_x / SCALE
    y = world_y / SCALE
    y = max(0, min(1, y))
    
    lon = x * 360 - 180
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y)))
    lat = math.degrees(lat_rad)
    
    return lat, lon

def process_google_features(maps_data):
    """Process Google Maps features into location list"""
    locations = []
    seen = set()
    
    if not maps_data:
        return locations
    
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
            
            coord_key = (round(lat, 5), round(lon, 5), title)
            if coord_key not in seen:
                seen.add(coord_key)
                locations.append({
                    'title': title,
                    'lat': lat,
                    'lon': lon,
                    'type': 'poi'
                })
    
    return locations

def load_zones_data():
    """Load zone data from geopackage"""
    print("\n🗺️  Loading zones data...")
    try:
        conn = sqlite3.connect('/mnt/user-data/uploads/zone_attributes_synthetic_.gpkg')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT zone_id, MESO, MACRO, tot_jobs, population 
            FROM 'zone_attributes_synthetic ' 
            LIMIT 100
        """)
        zones = cursor.fetchall()
        
        conn.close()
        print(f"   ✅ Loaded {len(zones)} zones")
        return zones
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

# =============================================================================
# STEP 2: GENERATE INTERACTIVE MAP HTML
# =============================================================================

def generate_map_html(locations, zones, bus_data):
    """Generate complete interactive map"""
    
    # Prepare zone data for display
    zones_html = ""
    if zones:
        zones_html = "<h4>Top 10 Zones by Population</h4><ul>"
        sorted_zones = sorted(zones, key=lambda x: x[4], reverse=True)[:10]
        for z in sorted_zones:
            zones_html += f"<li><strong>{z[2]}</strong> ({z[1]}): {z[4]:,} people, {z[3]:,} jobs</li>"
        zones_html += "</ul>"
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Baku Integrated Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        #container {{ display: flex; height: 100vh; }}
        
        /* Sidebar */
        #sidebar {{
            width: 380px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            overflow-y: auto;
            box-shadow: 4px 0 10px rgba(0,0,0,0.3);
            z-index: 1000;
        }}
        
        .sidebar-header {{
            padding: 25px;
            background: rgba(0,0,0,0.2);
            border-bottom: 2px solid rgba(255,255,255,0.3);
        }}
        
        .sidebar-header h1 {{
            font-size: 24px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .sidebar-header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            padding: 20px;
            background: rgba(0,0,0,0.1);
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .stat-number {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 12px;
            opacity: 0.8;
        }}
        
        .search-box {{
            padding: 20px;
            background: rgba(0,0,0,0.1);
        }}
        
        .search-box input {{
            width: 100%;
            padding: 12px 15px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            background: rgba(255,255,255,0.9);
            transition: all 0.3s;
        }}
        
        .search-box input:focus {{
            outline: none;
            background: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        
        .location-list {{
            padding: 15px;
        }}
        
        .location-item {{
            background: rgba(255,255,255,0.1);
            padding: 14px 16px;
            margin-bottom: 10px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            border-left: 4px solid #4CAF50;
            backdrop-filter: blur(10px);
        }}
        
        .location-item:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
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
        
        .zone-info {{
            padding: 20px;
            background: rgba(0,0,0,0.2);
            margin: 15px;
            border-radius: 8px;
        }}
        
        .zone-info h4 {{
            margin-bottom: 10px;
            font-size: 16px;
        }}
        
        .zone-info ul {{
            list-style: none;
        }}
        
        .zone-info li {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            font-size: 13px;
        }}
        
        #map {{ flex: 1; }}
        
        .leaflet-popup-content {{
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        .popup-title {{
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 5px;
            color: #333;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <div class="sidebar-header">
                <h1>🗺️ Baku Integrated Map</h1>
                <p>Real-time city data visualization</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(locations)}</div>
                    <div class="stat-label">📍 POI Locations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(zones)}</div>
                    <div class="stat-label">🏘️ City Zones</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(z[4] for z in zones):,}</div>
                    <div class="stat-label">👥 Population</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(z[3] for z in zones):,}</div>
                    <div class="stat-label">💼 Total Jobs</div>
                </div>
            </div>
            
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 Search locations..." />
            </div>
            
            <div class="location-list" id="locationList"></div>
            
            <div class="zone-info">
                {zones_html}
            </div>
        </div>
        
        <div id="map"></div>
    </div>

    <script>
        // Initialize map
        var map = L.map('map').setView([40.4093, 49.8671], 11);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }}).addTo(map);
        
        // Location data
        var locations = {json.dumps(locations, ensure_ascii=False)};
        var markers = {{}};
        
        // Add markers
        locations.forEach(function(loc, idx) {{
            loc.id = idx;
            var marker = L.marker([loc.lat, loc.lon], {{
                icon: L.icon({{
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }})
            }}).addTo(map);
            
            marker.bindPopup('<div class="popup-title">' + loc.title + '</div>');
            markers[idx] = marker;
            
            marker.on('click', function() {{
                highlightLocation(idx);
            }});
        }});
        
        // Render location list
        function renderList(filteredLocations) {{
            var listHtml = '';
            filteredLocations.forEach(function(loc) {{
                listHtml += 
                    '<div class="location-item" data-id="' + loc.id + '" onclick="flyToLocation(' + loc.id + ')">' +
                    '<div class="location-title">📍 ' + loc.title + '</div>' +
                    '<div class="location-coords">' + loc.lat.toFixed(5) + ', ' + loc.lon.toFixed(5) + '</div>' +
                    '</div>';
            }});
            document.getElementById('locationList').innerHTML = listHtml;
        }}
        
        renderList(locations);
        
        // Search
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            var term = e.target.value.toLowerCase();
            var filtered = locations.filter(function(loc) {{
                return loc.title.toLowerCase().includes(term);
            }});
            renderList(filtered);
        }});
        
        // Fly to location
        function flyToLocation(id) {{
            var loc = locations[id];
            map.flyTo([loc.lat, loc.lon], 15, {{ duration: 1.5 }});
            markers[id].openPopup();
            highlightLocation(id);
        }}
        
        // Highlight
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
    
    return html

# =============================================================================
# MAIN EXECUTION
# =============================================================================

# Fetch data
maps_data = fetch_google_maps_features()
bus_data = fetch_bus_data()
zones = load_zones_data()

# Process locations
locations = process_google_features(maps_data)
print(f"\n✅ Processed {len(locations)} POI locations")

# Generate map
print("\n🎨 Generating interactive map...")
html_content = generate_map_html(locations, zones, bus_data)

# Save
with open('baku_complete_map.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("\n" + "=" * 80)
print("✅ VISUALIZATION COMPLETE!")
print("=" * 80)
print("\n📂 Output: baku_complete_map.html")
print("\n📊 Data Summary:")
print(f"   • POI Locations: {len(locations)}")
print(f"   • City Zones: {len(zones)}")
if zones:
    print(f"   • Total Population: {sum(z[4] for z in zones):,}")
    print(f"   • Total Jobs: {sum(z[3] for z in zones):,}")
print("\n🌐 Open 'baku_complete_map.html' in your browser to view the map!")
