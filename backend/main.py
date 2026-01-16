from fastapi import FastAPI, HTTPException, Query, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import pandas as pd
import geopandas as gpd
import json
import requests
import math

app = FastAPI(title="Transportation Data API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bus_data: Optional[pd.DataFrame] = None
geo_data: Optional[gpd.GeoDataFrame] = None

def load_bus_data():
    global bus_data
    try:
        bus_data = pd.read_csv("ceck_in_buss.csv")
        bus_data['Date'] = pd.to_datetime(bus_data['Date'])
        print(f"✓ Loaded {len(bus_data)} bus records")
        return True
    except Exception as e:
        print(f"Error loading bus data: {e}")
        return False

def load_geo_data():
    global geo_data
    try:
        geo_data = gpd.read_file("zone_attributes_synthetic.gpkg")
        print(f"✓ Loaded {len(geo_data)} geographic zones")
        return True
    except Exception as e:
        print(f"Error loading geo data: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    load_bus_data()
    load_geo_data()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "bus_data_loaded": bus_data is not None,
        "geo_data_loaded": geo_data is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/bus/registrations")
async def get_bus_registrations(
    route: Optional[str] = None,
    operator: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=1000, le=10000),
    offset: int = Query(default=0, ge=0)
):
    if bus_data is None:
        raise HTTPException(status_code=503, detail="Bus data not loaded")
    
    df = bus_data.copy()
    if route:
        df = df[df['Route'] == route]
    if operator:
        df = df[df['Operator'] == operator]
    if start_date:
        df = df[df['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Date'] <= pd.to_datetime(end_date)]
    
    df = df.iloc[offset:offset + limit]
    
    records = []
    for _, row in df.iterrows():
        records.append({
            "Date": row['Date'].isoformat(),
            "Hour": int(row['Hour']),
            "Route": str(row['Route']),
            "Total Count": int(row['Total Count']),
            "By SmartCard": int(row['By SmartCard']),
            "By QR": int(row['By QR']),
            "Number Of Busses": int(row['Number Of Busses']),
            "Operator": row['Operator']
        })
    
    return {"data": records, "total": len(bus_data)}

@app.get("/api/bus/stats")
async def get_bus_stats():
    if bus_data is None:
        raise HTTPException(status_code=503, detail="Bus data not loaded")
    
    return {
        "total_records": len(bus_data),
        "date_range": {
            "start": bus_data['Date'].min().isoformat(),
            "end": bus_data['Date'].max().isoformat()
        },
        "routes_count": bus_data['Route'].nunique(),
        "operators": bus_data['Operator'].unique().tolist(),
        "total_passengers": int(bus_data['Total Count'].sum())
    }

@app.get("/api/bus/analytics")
async def get_bus_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    hour_start: Optional[int] = None,
    hour_end: Optional[int] = None,
    companies: Optional[str] = None,
    routes: Optional[str] = None
):
    if bus_data is None:
        raise HTTPException(status_code=503, detail="Bus data not loaded")
    
    df = bus_data.copy()
    
    if start_date:
        df = df[df['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Date'] <= pd.to_datetime(end_date)]
    if hour_start is not None:
        df = df[df['Hour'] >= hour_start]
    if hour_end is not None:
        df = df[df['Hour'] <= hour_end]
    if companies:
        company_list = companies.split(',')
        df = df[df['Operator'].isin(company_list)]
    if routes:
        route_list = routes.split(',')
        df = df[df['Route'].isin(route_list)]
    
    total_passengers = int(df['Total Count'].sum())
    total_buses = int(df['Number Of Busses'].sum())
    avg_pass_per_bus = total_passengers / total_buses if total_buses > 0 else 0
    
    hourly = df.groupby('Hour')['Total Count'].sum()
    peak_hour = int(hourly.idxmax()) if len(hourly) > 0 else 0
    
    by_company = df.groupby('Operator').agg({
        'Total Count': 'sum',
        'Number Of Busses': 'sum'
    })
    by_company['pass_per_bus'] = by_company['Total Count'] / by_company['Number Of Busses']
    most_efficient = by_company['pass_per_bus'].idxmax() if len(by_company) > 0 else "N/A"
    
    by_company_payment = df.groupby('Operator').agg({
        'By SmartCard': 'sum',
        'Total Count': 'sum'
    })
    by_company_payment['smartcard_pct'] = (by_company_payment['By SmartCard'] / by_company_payment['Total Count'] * 100)
    payment_leader = by_company_payment['smartcard_pct'].idxmax() if len(by_company_payment) > 0 else "N/A"
    
    company_agg = df.groupby('Operator').agg({
        'Total Count': 'sum',
        'Number Of Busses': 'sum',
        'By SmartCard': 'sum',
        'By QR': 'sum'
    }).reset_index()
    company_agg['pass_per_bus'] = company_agg['Total Count'] / company_agg['Number Of Busses']
    
    route_agg = df.groupby('Route').agg({
        'Total Count': 'sum',
        'Number Of Busses': 'sum',
        'By SmartCard': 'sum',
        'By QR': 'sum',
        'Operator': 'first'
    }).reset_index()
    route_agg['pass_per_bus'] = route_agg['Total Count'] / route_agg['Number Of Busses']
    
    hour_agg = df.groupby('Hour').agg({
        'Total Count': 'sum',
        'Number Of Busses': 'sum',
        'By SmartCard': 'sum',
        'By QR': 'sum'
    }).reset_index()
    hour_agg['pass_per_bus'] = hour_agg['Total Count'] / hour_agg['Number Of Busses']
    
    top_routes = route_agg.nlargest(15, 'Total Count')
    bottom_routes = route_agg.nsmallest(5, 'pass_per_bus')
    
    unique_companies = sorted(df['Operator'].unique().tolist())
    unique_routes = sorted(df['Route'].unique().tolist())
    unique_hours = sorted(df['Hour'].unique().tolist())
    unique_dates = sorted(df['Date'].dt.strftime('%Y-%m-%d').unique().tolist())
    
    return {
        "kpis": {
            "total_passengers": total_passengers,
            "total_buses": total_buses,
            "avg_pass_per_bus": round(avg_pass_per_bus, 1),
            "peak_hour": peak_hour,
            "most_efficient_company": most_efficient,
            "payment_leader": payment_leader
        },
        "by_company": company_agg.to_dict('records'),
        "by_route": route_agg.to_dict('records'),
        "by_hour": hour_agg.to_dict('records'),
        "top_routes": top_routes.to_dict('records'),
        "bottom_routes": bottom_routes.to_dict('records'),
        "dropdowns": {
            "companies": unique_companies,
            "routes": unique_routes,
            "hours": unique_hours,
            "dates": unique_dates
        }
    }

@app.get("/api/bus/routes")
async def get_bus_routes():
    if bus_data is None:
        raise HTTPException(status_code=503, detail="Bus data not loaded")
    
    route_agg = bus_data.groupby('Route').agg({
        'Total Count': 'sum',
        'Number Of Busses': 'sum',
        'Operator': 'first'
    }).reset_index()
    
    return route_agg.nlargest(20, 'Total Count').to_dict('records')

@app.get("/api/bus/operators")
async def get_bus_operators():
    if bus_data is None:
        raise HTTPException(status_code=503, detail="Bus data not loaded")
    
    operator_agg = bus_data.groupby('Operator').agg({
        'Total Count': 'sum',
        'Number Of Busses': 'sum'
    }).reset_index()
    operator_agg.columns = ['Operator', 'Total_Passengers', 'Total_Buses']
    
    return operator_agg.to_dict('records')

@app.get("/api/bus/volume")
async def get_bus_volume(group_by: str = "route"):
    if bus_data is None:
        raise HTTPException(status_code=503, detail="Bus data not loaded")
    
    if group_by == "route":
        group_col = 'Route'
    elif group_by == "hour":
        group_col = 'Hour'
    elif group_by == "operator":
        group_col = 'Operator'
    else:
        group_col = 'Route'
    
    volume_agg = bus_data.groupby(group_col).agg({
        'Total Count': 'sum',
        'By SmartCard': 'sum',
        'By QR': 'sum',
        'Number Of Busses': 'sum'
    }).reset_index()
    
    return volume_agg.to_dict('records')

@app.get("/api/bus/hourly-trend")
async def get_hourly_trend(route: Optional[str] = None):
    if bus_data is None:
        raise HTTPException(status_code=503, detail="Bus data not loaded")
    
    df = bus_data.copy()
    
    if route:
        df = df[df['Route'] == route]
    
    hourly = df.groupby('Hour').agg({
        'Total Count': 'sum',
        'By SmartCard': 'sum',
        'By QR': 'sum',
        'Number Of Busses': 'sum'
    }).reset_index()
    
    return hourly.to_dict('records')

@app.get("/api/demographics/{region_type}")
async def get_demographics(
    region_type: str = PathParam(..., regex="^(micro|meso|macro)$")
):
    if geo_data is None:
        raise HTTPException(status_code=503, detail="Geo data not loaded")
    
    region_column_map = {
        "micro": "MICRO",
        "meso": "MESO",
        "macro": "MACRO"
    }
    
    region_col = region_column_map[region_type]
    
    dissolved = geo_data.dissolve(by=region_col, aggfunc={
        'population': 'sum',
        'tot_jobs': 'sum'
    }).reset_index()
    
    features = []
    for idx, row in dissolved.iterrows():
        geom_json = json.loads(gpd.GeoSeries([row['geometry']]).to_json())['features'][0]['geometry']
        
        feature = {
            "type": "Feature",
            "id": idx,
            "geometry": geom_json,
            "properties": {
                "region_name": str(row[region_col]),
                "population": float(row['population']) if pd.notna(row['population']) else 0,
                "tot_jobs": float(row['tot_jobs']) if pd.notna(row['tot_jobs']) else 0,
                "region_type": region_type
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.get("/api/demographics/stats/{region_type}")
async def get_demographics_stats(
    region_type: str = PathParam(..., regex="^(micro|meso|macro)$")
):
    if geo_data is None:
        raise HTTPException(status_code=503, detail="Geo data not loaded")
    
    region_column_map = {
        "micro": "MICRO",
        "meso": "MESO",
        "macro": "MACRO"
    }
    
    region_col = region_column_map[region_type]
    
    dissolved = geo_data.dissolve(by=region_col, aggfunc={
        'population': 'sum',
        'tot_jobs': 'sum'
    }).reset_index()
    
    stats = {
        "total_zones": len(dissolved),
        "region_type": region_type,
        "population": {
            "total": float(dissolved['population'].sum()),
            "mean": float(dissolved['population'].mean()),
            "min": float(dissolved['population'].min()),
            "max": float(dissolved['population'].max())
        },
        "jobs": {
            "total": float(dissolved['tot_jobs'].sum()),
            "mean": float(dissolved['tot_jobs'].mean()),
            "min": float(dissolved['tot_jobs'].min()),
            "max": float(dissolved['tot_jobs'].max())
        }
    }
    
    return stats

def google_coords_to_latlon(world_x, world_y):
    map_size = 256 * (2 ** 23)
    x = world_x / map_size
    y = world_y / map_size
    lon = x * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))
    return lat, lon

def fetch_and_save_route_data():
    headers_maps = {
        'accept': '*/*',
        'origin': 'https://map.ayna.gov.az',
        'referer': 'https://map.ayna.gov.az/',
        'user-agent': 'Mozilla/5.0',
    }
    
    url_maps = 'https://mapsresources-pa.googleapis.com/v1/featureMaps?map_id=47b57ca3c234946a&version=17854301209442801430&pb=!1m4!1m3!1i12!2i2613!3i1543!1m4!1m3!1i12!2i2614!3i1543!1m4!1m3!1i12!2i2615!3i1543!1m4!1m3!1i12!2i2613!3i1544!1m4!1m3!1i12!2i2613!3i1545!1m4!1m3!1i12!2i2614!3i1544!1m4!1m3!1i12!2i2614!3i1545!1m4!1m3!1i12!2i2615!3i1544!1m4!1m3!1i12!2i2615!3i1545!1m4!1m3!1i12!2i2616!3i1543!1m4!1m3!1i12!2i2617!3i1543!1m4!1m3!1i12!2i2616!3i1544!1m4!1m3!1i12!2i2616!3i1545!1m4!1m3!1i12!2i2617!3i1544!1m4!1m3!1i12!2i2617!3i1545!2m3!1e0!2sm!3i762526034!3m13!2str-TR!3sUS!5e18!12m5!1e68!2m2!1sset!2sRoadmap!4e2!12m3!1e37!2m1!1ssmartmaps!4e3!12m1!5b1!23i46991212!23i47054750!23i47083502!23i56565656!26m2!1e2!1e3'
    
    poi_locations = []
    try:
        response = requests.get(url_maps, headers=headers_maps, timeout=15)
        maps_data = response.json()
        
        for tile in maps_data:
            base = tile.get('base', [None, None])
            if not base[0]:
                continue
            
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
                    poi_locations.append({'title': title, 'lat': lat, 'lon': lon})
    except Exception as e:
        print(f"POI error: {e}")
    
    headers_bus = {
        'Accept': 'application/json',
        'Origin': 'https://map.ayna.gov.az',
        'Referer': 'https://map.ayna.gov.az/',
        'User-Agent': 'Mozilla/5.0',
    }
    
    response = requests.get('https://map-api.ayna.gov.az/api/bus/getBusList', headers=headers_bus)
    bus_list = response.json()
    
    all_bus_data = []
    all_stops = []
    route_paths_flat = []
    
    for bus in bus_list:
        bus_id = bus['id']
        bus_number = bus['number']
        
        try:
            response = requests.get(
                'https://map-api.ayna.gov.az/api/bus/getBusById',
                params={'id': bus_id},
                headers=headers_bus,
                timeout=10
            )
            
            if response.status_code == 200:
                bus_detail = response.json()
                
                stops = bus_detail.get('stops', [])
                for stop_data in stops:
                    stop_info = stop_data.get('stop', {})
                    lat = stop_info.get('latitude')
                    lon = stop_info.get('longitude')
                    name = stop_info.get('name', stop_data.get('stopName', 'Unknown'))
                    
                    if lat and lon:
                        all_stops.append({
                            'bus_id': bus_id,
                            'bus_number': bus_number,
                            'stop_name': name,
                            'lat': float(lat),
                            'lon': float(lon),
                        })
                
                route_paths = bus_detail.get('routes', [])
                for route in route_paths:
                    if 'coordinatesList' in route:
                        for coord in route['coordinatesList']:
                            route_paths_flat.append({
                                'bus_id': bus_id,
                                'bus_number': bus_number,
                                'lat': coord.get('lat'),
                                'lon': coord.get('lng')
                            })
                
                all_bus_data.append({
                    'id': bus_id,
                    'number': bus_number,
                    'firstPoint': bus_detail.get('firstPoint', ''),
                    'lastPoint': bus_detail.get('lastPoint', ''),
                    'duration': bus_detail.get('durationMinuts', 0),
                    'stops_count': len(stops)
                })
        except Exception as e:
            print(f"Error bus {bus_id}: {e}")
    
    pd.DataFrame(poi_locations).to_csv('pois.csv', index=False)
    pd.DataFrame(all_stops).to_csv('bus_stops.csv', index=False)
    pd.DataFrame(all_bus_data).to_csv('bus_routes.csv', index=False)
    pd.DataFrame(route_paths_flat).to_csv('bus_route_paths.csv', index=False)
    
    return {
        "pois": len(poi_locations),
        "buses": len(all_bus_data),
        "stops": len(all_stops),
        "paths": len(route_paths_flat)
    }

@app.get("/api/routes/live")
async def get_live_routes():
    try:
        df_pois = pd.read_csv("pois.csv")
        df_stops = pd.read_csv("bus_stops.csv")
        df_buses = pd.read_csv("bus_routes.csv")
        
        try:
            df_routes = pd.read_csv("bus_route_paths.csv")
        except:
            df_routes = pd.DataFrame()
        
        pois = df_pois.to_dict('records')
        stops = df_stops.to_dict('records')
        buses = df_buses.to_dict('records')
        
        route_paths = {}
        if not df_routes.empty:
            for bus_id in df_routes['bus_id'].unique():
                bus_routes = df_routes[df_routes['bus_id'] == bus_id]
                route_paths[int(bus_id)] = bus_routes[['lat', 'lon']].to_dict('records')
        
        return {
            "pois": pois,
            "stops": stops,
            "buses": buses,
            "route_paths": route_paths
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"CSV files not found. Click 'Refresh Live Data'. Error: {str(e)}")

@app.post("/api/routes/refresh")
async def refresh_route_data():
    try:
        result = fetch_and_save_route_data()
        return {
            "status": "success",
            "message": "Route data refreshed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
