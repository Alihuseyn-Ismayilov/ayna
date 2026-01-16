"""
COMPLETE BAKU MAP VISUALIZATION
Includes: POIs, Zone Demographics, Bus Routes/Stops
"""

import requests
import json
import math
import sqlite3

print("=" * 80)
print("🗺️  BAKU COMPLETE MAP - ALL DATA LAYERS")
print("=" * 80)

# ============================================================================
# COORDINATE CONVERSION (Zoom Level 23)
# ============================================================================
def google_coords_to_latlon(world_x, world_y):
    map_size = 256 * (2 ** 23)
    x = world_x / map_size
    y = world_y / map_size
    lon = x * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))
    return lat, lon

# ============================================================================
# 1. FETCH POI LOCATIONS
# ============================================================================
def fetch_poi_locations():
    print("\n📍 Fetching POI locations...")
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
        for tile in maps_data:
            base = tile.get('base', [None, None])
            if not base[0]: continue
            
            for feature in tile.get('features', []):
                try:
                    c_data = json.loads(feature.get('c', '{}'))
                    title = c_data.get('1', {}).get('title', 'Unknown')
                except:
                    title = 'Unknown'
                
                coords = feature.get('a', [])
                world_x = base[0] + (coords[0] if len(coords) > 0 else 0)
                world_y = base[1] + (coords[1] if len(coords) > 1 else 0)
                
                lat, lon = google_coords_to_latlon(world_x, world_y)
                
                if 40.0 <= lat <= 41.0 and 49.0 <= lon <= 51.0:
                    locations.append({
                        'id': len(locations),
                        'title': title,
                        'lat': lat,
                        'lon': lon,
                        'type': 'poi'
                    })
        
        print(f"   ✅ Fetched {len(locations)} POI locations")
        return locations
    except Exception as e:
        print(f"   ⚠️  Could not fetch: {e}")
        return []

# ============================================================================
# 2. FETCH BUS DATA
# ============================================================================
def fetch_bus_data():
    print("\n🚌 Fetching bus data...")
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://map.ayna.gov.az',
        'Referer': 'https://map.ayna.gov.az/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        response = requests.get('https://map-api.ayna.gov.az/api/bus/getBusList', 
                               headers=headers, timeout=15)
        response.raise_for_status()
        bus_data = response.json()
        
        # Process bus data based on structure
        buses = []
        if isinstance(bus_data, list):
            for item in bus_data:
                # Extract bus info (structure may vary)
                bus_info = {
                    'id': item.get('id', item.get('busId', len(buses))),
                    'name': item.get('name', item.get('routeName', f"Bus {len(buses)+1}")),
                    'number': item.get('number', item.get('routeNumber', '')),
                    'lat': item.get('lat', item.get('latitude', None)),
                    'lon': item.get('lon', item.get('longitude', None)),
                    'type': 'bus'
                }
                
                # Only add if has coordinates
                if bus_info['lat'] and bus_info['lon']:
                    buses.append(bus_info)
        
        print(f"   ✅ Fetched {len(buses)} bus items")
        return buses
    except Exception as e:
        print(f"   ⚠️  Could not fetch: {e}")
        return []

# ============================================================================
# 3. LOAD ZONE DATA
# ============================================================================
def load_zone_data():
    print("\n🏘️  Loading zone data...")
    try:
        conn = sqlite3.connect('/mnt/user-data/uploads/zone_attributes_synthetic_.gpkg')
        cursor = conn.cursor()
        
        # Get all zones with their data
        cursor.execute("""
            SELECT zone_id, MICRO, MESO, MACRO, tot_jobs, population
            FROM 'zone_attributes_synthetic '
        """)
        zones = cursor.fetchall()
        
        # Get statistics by MACRO area
        cursor.execute("""
            SELECT MACRO, COUNT(*) as count, SUM(population) as pop, SUM(tot_jobs) as jobs
            FROM 'zone_attributes_synthetic '
            WHERE MACRO IS NOT NULL
            GROUP BY MACRO
            ORDER BY pop DESC
        """)
        macro_stats = cursor.fetchall()
        
        conn.close()
        
        zone_list = []
        for z in zones:
            zone_list.append({
                'zone_id': int(z[0]) if z[0] else 0,
                'micro': int(z[1]) if z[1] else 0,
                'meso': z[2],
                'macro': z[3],
                'jobs': int(z[4]) if z[4] else 0,
                'population': int(z[5]) if z[5] else 0
            })
        
        print(f"   ✅ Loaded {len(zone_list)} zones from {len(macro_stats)} areas")
        
        return zone_list, macro_stats
    except Exception as e:
        print(f"   ⚠️  Could not load: {e}")
        return [], []

# ============================================================================
# 4. GENERATE COMPLETE MAP
# ============================================================================
def generate_complete_map(poi_locations, bus_data, zones, macro_stats):
    print("\n🎨 Generating complete interactive map...")
    
    total_pop = sum(z['population'] for z in zones)
    total_jobs = sum(z['jobs'] for z in zones)
    
    # Build macro stats HTML
    macro_html = "<h4>📊 Areas by Population</h4><div style='max-height:300px;overflow-y:auto'>"
    for stat in macro_stats[:15]:
        macro_html += f"""
        <div style='padding:10px;margin:5px 0;background:rgba(255,255,255,0.1);border-radius:5px;'>
            <strong>{stat[0]}</strong><br>
            <small>{stat[1]} zones • {stat[2]:,} people • {stat[3]:,} jobs</small>
        </div>
        """
    macro_html += "</div>"
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Baku Complete Map - All Data</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        #container {{ display: flex; height: 100vh; }}
        
        #sidebar {{
            width: 400px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            overflow-y: auto;
            box-shadow: 4px 0 15px rgba(0,0,0,0.3);
            z-index: 1000;
        }}
        
        .header {{
            padding: 25px;
            background: rgba(0,0,0,0.3);
            border-bottom: 2px solid rgba(255,255,255,0.2);
        }}
        
        .header h1 {{
            font-size: 24px;
            margin-bottom: 8px;
            font-weight: 700;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            padding: 20px;
            background: rgba(0,0,0,0.2);
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.15);
            padding: 18px;
            border-radius: 12px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-3px);
            background: rgba(255,255,255,0.2);
        }}
        
        .stat-number {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 12px;
            opacity: 0.85;
        }}
        
        .controls {{
            padding: 20px;
            background: rgba(0,0,0,0.15);
        }}
        
        .layer-toggle {{
            background: rgba(255,255,255,0.1);
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .layer-toggle:hover {{
            background: rgba(255,255,255,0.2);
        }}
        
        .layer-toggle input {{
            width: 20px;
            height: 20px;
        }}
        
        .search-box {{
            padding: 20px;
            background: rgba(0,0,0,0.15);
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
        
        .info-section {{
            padding: 20px;
            background: rgba(0,0,0,0.2);
            margin: 15px;
            border-radius: 10px;
        }}
        
        .info-section h4 {{
            margin-bottom: 15px;
            font-size: 16px;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 8px;
        }}
        
        #map {{ flex: 1; }}
        
        .leaflet-popup-content {{
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <div class="header">
                <h1>🗺️ Baku Complete Map</h1>
                <p>POIs • Zones • Transportation</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(poi_locations)}</div>
                    <div class="stat-label">📍 POI Locations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(bus_data)}</div>
                    <div class="stat-label">🚌 Bus Items</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(zones)}</div>
                    <div class="stat-label">🏘️ City Zones</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(macro_stats)}</div>
                    <div class="stat-label">🏙️ Areas</div>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_pop:,}</div>
                    <div class="stat-label">👥 Total Population</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_jobs:,}</div>
                    <div class="stat-label">💼 Total Jobs</div>
                </div>
            </div>
            
            <div class="controls">
                <h4 style="margin-bottom:12px;">🔧 Map Layers</h4>
                <label class="layer-toggle">
                    <input type="checkbox" id="togglePOI" checked>
                    <span>📍 POI Locations</span>
                </label>
                <label class="layer-toggle">
                    <input type="checkbox" id="toggleBus" checked>
                    <span>🚌 Bus Data</span>
                </label>
            </div>
            
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 Search locations..." />
            </div>
            
            <div class="location-list" id="locationList"></div>
            
            <div class="info-section">
                {macro_html}
            </div>
        </div>
        
        <div id="map"></div>
    </div>

    <script>
        var map = L.map('map').setView([40.4093, 49.8671], 11);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap',
            maxZoom: 19
        }}).addTo(map);
        
        // Data
        var pois = {json.dumps(poi_locations, ensure_ascii=False)};
        var buses = {json.dumps(bus_data, ensure_ascii=False)};
        var allLocations = pois.concat(buses);
        
        var poiMarkers = [];
        var busMarkers = [];
        
        // Add POI markers
        pois.forEach(function(loc, idx) {{
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
            
            marker.bindPopup('<div style="font-weight:bold; font-size:14px;">📍 ' + loc.title + '</div>');
            poiMarkers.push(marker);
            
            marker.on('click', function() {{ highlightLocation(idx); }});
        }});
        
        // Add bus markers
        buses.forEach(function(bus, idx) {{
            var marker = L.marker([bus.lat, bus.lon], {{
                icon: L.icon({{
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }})
            }}).addTo(map);
            
            marker.bindPopup('<div style="font-weight:bold; font-size:14px;">🚌 ' + bus.name + '</div>');
            busMarkers.push(marker);
        }});
        
        // Layer toggles
        document.getElementById('togglePOI').addEventListener('change', function(e) {{
            poiMarkers.forEach(m => e.target.checked ? map.addLayer(m) : map.removeLayer(m));
        }});
        
        document.getElementById('toggleBus').addEventListener('change', function(e) {{
            busMarkers.forEach(m => e.target.checked ? map.addLayer(m) : map.removeLayer(m));
        }});
        
        // Render location list
        function renderList(locs) {{
            var html = '';
            locs.forEach(function(loc) {{
                var icon = loc.type === 'bus' ? '🚌' : '📍';
                html += '<div class="location-item" data-id="' + loc.id + '" onclick="flyTo(' + loc.id + ', \\'' + loc.type + '\\')">' +
                    '<div class="location-title">' + icon + ' ' + loc.title + '</div>' +
                    '<div class="location-coords">' + loc.lat.toFixed(5) + ', ' + loc.lon.toFixed(5) + '</div>' +
                    '</div>';
            }});
            document.getElementById('locationList').innerHTML = html || '<p style="text-align:center;padding:20px;opacity:0.7;">No results</p>';
        }}
        
        renderList(pois);
        
        // Search
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            var term = e.target.value.toLowerCase();
            var filtered = pois.filter(l => l.title.toLowerCase().includes(term));
            renderList(filtered);
        }});
        
        // Fly to location
        function flyTo(id, type) {{
            var markers = type === 'bus' ? busMarkers : poiMarkers;
            var loc = type === 'bus' ? buses[id] : pois[id];
            map.flyTo([loc.lat, loc.lon], 16, {{ duration: 1.5 }});
            if (markers[id]) markers[id].openPopup();
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
    
    with open('baku_complete_map.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("   ✅ Map saved: baku_complete_map.html")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

poi_locations = fetch_poi_locations()
bus_data = fetch_bus_data()
zones, macro_stats = load_zone_data()

generate_complete_map(poi_locations, bus_data, zones, macro_stats)

print("\n" + "=" * 80)
print("✅ COMPLETE! Open 'baku_complete_map.html' in your browser")
print("=" * 80)
print(f"\n📊 Data Summary:")
print(f"   • POI Locations: {len(poi_locations)}")
print(f"   • Bus Items: {len(bus_data)}")
print(f"   • City Zones: {len(zones)}")
print(f"   • Total Population: {sum(z['population'] for z in zones):,}")
print(f"   • Total Jobs: {sum(z['jobs'] for z in zones):,}")
