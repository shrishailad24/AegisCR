import sqlite3
import os
import requests
import json
from functools import lru_cache

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vehicles.db"))

VEHICLE_SEED_DATA = [
    ("Mahindra", "Thar ROXX", "AX7L 4WD Diesel MT", 2024, "SUV", "Diesel", "Manual", "2184 cc", "SUV", 1899000, 2165000),
    ("Mahindra", "Thar ROXX", "MX3 Petrol AT", 2024, "SUV", "Petrol", "Automatic", "1997 cc", "SUV", 1499000, 1708000),
    ("Mahindra", "XUV700", "AX7 Luxury Pack Petrol AT", 2024, "SUV", "Petrol", "Automatic", "1997 cc", "SUV", 2399000, 2785000),
    ("Mahindra", "Scorpio-N", "Z8L Diesel 4WD", 2024, "SUV", "Diesel", "Manual", "2184 cc", "SUV", 2249000, 2599000),
    ("Tata", "Nexon EV", "Empowered Plus LR", 2024, "Electric Vehicle (EV)", "Electric", "Automatic", "40.5 kWh", "SUV", 1699000, 1785000),
    ("Tata", "Curvv EV", "Empowered Plus 55kWh", 2024, "Electric Vehicle (EV)", "Electric", "Automatic", "55 kWh", "Coupe SUV", 1925000, 2020000),
    ("Tata", "Harrier", "Fearless Plus Dark AT", 2024, "SUV", "Diesel", "Automatic", "1956 cc", "SUV", 2449000, 2840000),
    ("Tata", "Punch EV", "Empowered Plus S", 2024, "Electric Vehicle (EV)", "Electric", "Automatic", "35 kWh", "Micro SUV", 1329000, 1395000),
    ("Tata", "Ace Gold", "Diesel BS6", 2024, "Commercial Vehicle", "Diesel", "Manual", "702 cc", "Mini Truck", 550000, 615000),
    ("Toyota", "Fortuner", "Legender 4x4 AT", 2024, "SUV", "Diesel", "Automatic", "2755 cc", "SUV", 4654000, 5480000),
    ("Toyota", "Innova Hycross", "ZX (O) Hybrid", 2024, "SUV", "Strong Hybrid", "e-CVT", "1987 cc", "MUV", 3098000, 3620000),
    ("Toyota", "Urban Cruiser Taisor", "V Turbo AT", 2024, "SUV", "Petrol", "Automatic", "998 cc", "Compact SUV", 1287000, 1480000),
    ("Hyundai", "Creta", "SX (O) 1.5 Turbo DCT", 2024, "SUV", "Petrol", "DCT", "1482 cc", "SUV", 2000000, 2320000),
    ("Hyundai", "Verna", "SX (O) 1.5 Turbo DCT", 2024, "Sedan", "Petrol", "DCT", "1482 cc", "Sedan", 1742000, 2010000),
    ("Maruti Suzuki", "Brezza", "ZXi Plus AT", 2024, "SUV", "Petrol", "Automatic", "1462 cc", "SUV", 1398000, 1610000),
    ("Maruti Suzuki", "Swift", "ZXi Plus AMT", 2024, "Car / Sedan", "Petrol", "AMT", "1197 cc", "Hatchback", 964000, 1105000),
    ("Maruti Suzuki", "Fronx", "Alpha Turbo 6AT", 2024, "SUV", "Petrol", "Automatic", "998 cc", "Crossover", 1297000, 1490000),
    ("BMW", "X5", "xDrive40i M Sport", 2024, "SUV", "Petrol", "Automatic", "2998 cc", "Luxury SUV", 9700000, 11200000),
    ("Audi", "Q7", "Technology 55 TFSI", 2024, "SUV", "Petrol", "Automatic", "2995 cc", "Luxury SUV", 9445000, 10900000),
    ("Mercedes-Benz", "E-Class", "E 220d Exclusive", 2024, "Car / Sedan", "Diesel", "Automatic", "1993 cc", "Luxury Sedan", 7890000, 9150000),
    ("Royal Enfield", "Himalayan 450", "Hanle Black", 2024, "Two Wheeler", "Petrol", "Manual", "452 cc", "Adventure", 298000, 345000),
    ("Royal Enfield", "Hunter 350", "Dapper Grey", 2024, "Two Wheeler", "Petrol", "Manual", "349 cc", "Roadster", 169000, 195000),
    ("TVS", "iQube ST", "5.1 kWh EV", 2024, "Two Wheeler", "Electric", "Automatic", "5.1 kWh", "Scooter", 185000, 195000)
]

def init_vehicle_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            variant TEXT,
            year INTEGER,
            category TEXT,
            fuel_type TEXT,
            transmission TEXT,
            engine_cc TEXT,
            body_type TEXT,
            ex_showroom_price REAL,
            on_road_price REAL
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO vehicles (brand, model, variant, year, category, fuel_type, transmission, engine_cc, body_type, ex_showroom_price, on_road_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, VEHICLE_SEED_DATA)
        conn.commit()
    conn.close()

init_vehicle_db()

HEADERS = {"User-Agent": "Mozilla/5.0"}

@lru_cache(maxsize=32)
def fetch_carquery_makes():
    """Fetch makes instantly from local master DB with cached CarQuery API enhancement."""
    makes = set()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT brand FROM vehicles ORDER BY brand ASC")
    local_makes = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    for m in local_makes:
        makes.add(m)
        
    try:
        url = "http://www.carqueryapi.com/api/0.3/?cmd=getMakes"
        r = requests.get(url, headers=HEADERS, timeout=0.5)
        if r.status_code == 200:
            data = r.json()
            if "Makes" in data:
                for item in data["Makes"]:
                    make_display = item.get("make_display") or item.get("make_id")
                    if make_display:
                        makes.add(make_display)
    except Exception:
        pass
        
    return sorted(list(makes))

@lru_cache(maxsize=128)
def fetch_carquery_models(make: str):
    """Fetch models instantly from local master DB with cached CarQuery API enhancement."""
    models = set()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT model FROM vehicles WHERE LOWER(brand) = LOWER(?) ORDER BY model ASC", (make,))
    local_models = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    for mod in local_models:
        models.add(mod)
        
    try:
        url = f"http://www.carqueryapi.com/api/0.3/?cmd=getModels&make={make.lower()}"
        r = requests.get(url, headers=HEADERS, timeout=0.5)
        if r.status_code == 200:
            data = r.json()
            if "Models" in data:
                for item in data["Models"]:
                    model_name = item.get("model_name")
                    if model_name:
                        models.add(model_name)
    except Exception:
        pass
        
    return sorted(list(models))

@lru_cache(maxsize=256)
def fetch_carquery_specs(make: str, model: str):
    """Fetch specifications instantly from local master DB or cached CarQuery API."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT brand, model, variant, year, category, fuel_type, transmission, engine_cc, body_type, ex_showroom_price, on_road_price
        FROM vehicles
        WHERE LOWER(brand) = LOWER(?) AND LOWER(model) LIKE LOWER(?)
        LIMIT 1
    """, (make, f"%{model}%"))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "source": "Vehicle Master Database",
            "brand": row[0],
            "model": row[1],
            "variant": row[2],
            "year": row[3],
            "category": row[4],
            "fuel_type": row[5],
            "transmission": row[6],
            "engine_cc": row[7],
            "body_type": row[8],
            "ex_showroom_price": row[9],
            "on_road_price": row[10]
        }
        
    try:
        url = f"http://www.carqueryapi.com/api/0.3/?cmd=getTrims&make={make.lower()}&model={model.lower()}"
        r = requests.get(url, headers=HEADERS, timeout=0.5)
        if r.status_code == 200:
            data = r.json()
            trims = data.get("Trims", [])
            if trims:
                trim = trims[0]
                return {
                    "source": "CarQuery API",
                    "brand": trim.get("model_make_id", make).title(),
                    "model": trim.get("model_name", model).title(),
                    "variant": trim.get("model_trim", "Standard Trim"),
                    "year": int(trim.get("model_year", 2024)),
                    "category": trim.get("model_body", "SUV"),
                    "fuel_type": trim.get("model_engine_type", "Petrol"),
                    "transmission": trim.get("model_transmission_type", "Automatic"),
                    "engine_cc": f"{trim.get('model_engine_cc', 1500)} cc",
                    "body_type": trim.get("model_body", "Sedan"),
                    "ex_showroom_price": 1200000.0,
                    "on_road_price": 1380000.0
                }
    except Exception:
        pass
        
    return {
        "source": "Default Specification Engine",
        "brand": make.title(),
        "model": model.title(),
        "variant": "Standard Variant",
        "year": 2024,
        "category": "SUV",
        "fuel_type": "Petrol",
        "transmission": "Manual",
        "engine_cc": "1498 cc",
        "body_type": "SUV",
        "ex_showroom_price": 1200000.0,
        "on_road_price": 1380000.0
    }
