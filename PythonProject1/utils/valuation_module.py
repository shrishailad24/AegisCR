import os
import pickle
import hashlib
import pandas as pd
import numpy as np
import sqlite3
import streamlit as st

# Database matching generate_dataset.py
GEO_DB = {
    "Karnataka": {
        "districts": {
            "Bengaluru Urban": {
                "villages": ["Whitefield", "Electronic City", "Kengeri", "Yelahanka", "Sarjapur"],
                "base_guidance": 3500,
                "market_multiplier": 2.5,
                "growth_rate": 0.12 # 12% annual appreciation
            },
            "Mysuru": {
                "villages": ["Gokulam", "Vijayanagar", "J P Nagar", "Hebbal", "Ramakrishnanagar"],
                "base_guidance": 1800,
                "market_multiplier": 1.8,
                "growth_rate": 0.08
            },
            "Dharwad": {
                "villages": ["Navanagar", "Sattur", "Vidyagiri", "Lakamanahalli", "Kelageri"],
                "base_guidance": 1200,
                "market_multiplier": 1.5,
                "growth_rate": 0.06
            }
        }
    },
    "Telangana": {
        "districts": {
            "Hyderabad": {
                "villages": ["Gachibowli", "Madhapur", "Jubilee Hills", "Banjara Hills", "Kondapur"],
                "base_guidance": 5000,
                "market_multiplier": 3.0,
                "growth_rate": 0.15
            },
            "Medchal-Malkajgiri": {
                "villages": ["Kompally", "Malkajgiri", "Medchal", "Alwal", "Medipally"],
                "base_guidance": 2200,
                "market_multiplier": 2.0,
                "growth_rate": 0.09
            },
            "Rangareddy": {
                "villages": ["Gandi Maisamma", "Narsingi", "Kokapet", "Puppalguda", "Rajendranagar"],
                "base_guidance": 3000,
                "market_multiplier": 2.3,
                "growth_rate": 0.11
            }
        }
    },
    "Maharashtra": {
        "districts": {
            "Mumbai Suburban": {
                "villages": ["Andheri", "Bandra", "Borivali", "Kurla", "Ghatkopar"],
                "base_guidance": 8000,
                "market_multiplier": 3.5,
                "growth_rate": 0.14
            },
            "Pune": {
                "villages": ["Hinjawadi", "Hadapsar", "Baner", "Kothrud", "Wakad"],
                "base_guidance": 3200,
                "market_multiplier": 2.2,
                "growth_rate": 0.10
            },
            "Nagpur": {
                "villages": ["Dharampeth", "Manish Nagar", "Somalwada", "Wardha Road", "Sitabuldi"],
                "base_guidance": 1500,
                "market_multiplier": 1.6,
                "growth_rate": 0.07
            }
        }
    },
    "Tamil Nadu": {
        "districts": {
            "Chennai": {
                "villages": ["Adyar", "Velachery", "Mylapore", "Tambaram", "Guindy"],
                "base_guidance": 4500,
                "market_multiplier": 2.8,
                "growth_rate": 0.11
            },
            "Coimbatore": {
                "villages": ["Peelamedu", "Gandhipuram", "R S Puram", "Saravanampatti", "Singanallur"],
                "base_guidance": 2000,
                "market_multiplier": 1.9,
                "growth_rate": 0.08
            },
            "Madurai": {
                "villages": ["Anna Nagar", "K K Nagar", "Othakadai", "Sellur", "Tallakulam"],
                "base_guidance": 1300,
                "market_multiplier": 1.5,
                "growth_rate": 0.06
            }
        }
    }
}

def get_hashed_rate(state, district, village, pincode, land_type):
    # Generates a stable and consistent circle rate & multiplier for other input parameters
    input_str = f"{state.strip().lower()}|{district.strip().lower()}|{village.strip().lower()}|{pincode.strip()}"
    h = hashlib.md5(input_str.encode()).hexdigest()
    seed_val = int(h, 16) % 10000
    
    # Base guidance value per sqft (range: 800 - 3800)
    base_guidance = 800 + (seed_val % 3000)
    
    # Land type multiplier
    type_multipliers = {
        "Residential": 1.0,
        "Commercial": 1.4,
        "Agricultural": 0.35,
        "Industrial": 1.1
    }
    mult = type_multipliers.get(land_type, 1.0)
    guidance = int(base_guidance * mult)
    
    # Market multiplier (range: 1.3 - 2.8)
    market_mult = 1.3 + ((seed_val % 15) / 10.0)
    
    # Appreciation rate (range: 5% - 13%)
    growth = 0.05 + ((seed_val % 9) / 100.0)
    
    return guidance, market_mult, growth

@st.cache_data
def lookup_db_guideline(district, taluk, village, land_type, survey_number=None):
    if not district or not village:
        return None
        
    db_paths = [
        os.path.join(os.path.dirname(__file__), "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "..", "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "..", "PythonProject1", "guidelines.db"),
        "guidelines.db",
        "PythonProject1/guidelines.db"
    ]
    db_path = None
    for p in db_paths:
        if os.path.exists(p):
            db_path = p
            break
            
    if not db_path:
        return None
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        rows = []
        # 0. Try to match by survey number if provided
        if survey_number:
            import re
            clean_survey = re.sub(r'[^\d/\-]', '', survey_number)
            if len(clean_survey) > 1:
                cursor.execute("""
                    SELECT rate_per_sqft, property_classification, original_unit
                    FROM guidelines
                    WHERE (district LIKE ? OR taluk_office LIKE ?) AND village_area LIKE ?
                """, (f"%{district}%", f"%{district}%", f"%{clean_survey}%"))
                rows = cursor.fetchall()
                
        # 1. Try precise match with taluk and village
        if not rows:
            t_query = f"%{taluk}%" if taluk else "%"
            cursor.execute("""
                SELECT rate_per_sqft, property_classification, original_unit
                FROM guidelines
                WHERE (district LIKE ? OR taluk_office LIKE ?) AND (taluk_office LIKE ? OR ?) AND village_area LIKE ?
            """, (f"%{district}%", f"%{district}%", t_query, taluk is None, f"%{village}%"))
            rows = cursor.fetchall()
        
        # 2. Fallback to just district and village
        if not rows:
            cursor.execute("""
                SELECT rate_per_sqft, property_classification, original_unit
                FROM guidelines
                WHERE (district LIKE ? OR taluk_office LIKE ?) AND village_area LIKE ?
            """, (f"%{district}%", f"%{district}%", f"%{village}%"))
            rows = cursor.fetchall()
            
        # 3. Fallback to district and taluk average
        if not rows:
            cursor.execute("""
                SELECT rate_per_sqft, property_classification, original_unit
                FROM guidelines
                WHERE district LIKE ? OR taluk_office LIKE ?
            """, (f"%{district}%", f"%{district}%"))
            rows = cursor.fetchall()
            
        if not rows:
            conn.close()
            return None
            
        # Classify rows to find the best match for land_type
        best_rate = None
        for r_item in rows:
            rate = r_item[0]
            classification = r_item[1]
            if rate is None or not classification:
                continue
            cls_lower = str(classification).lower()
            if land_type == "Agricultural" and any(k in cls_lower for k in ["dry", "soil", "wet", "bagayat"]):
                best_rate = float(rate)
                break
            elif land_type == "Residential" and any(k in cls_lower for k in ["residential", "gramathana", "approved", "site"]):
                best_rate = float(rate)
                break
            elif land_type == "Commercial" and any(k in cls_lower for k in ["commercial", "approved", "residential", "site"]):
                best_rate = float(rate) * 1.5
                break
            elif land_type == "Industrial" and any(k in cls_lower for k in ["industrial", "approved", "residential", "site"]):
                best_rate = float(rate) * 1.1
                break
                
        if best_rate is None:
            valid_rates = [float(r[0]) for r in rows if r[0] is not None]
            if valid_rates:
                best_rate = sum(valid_rates) / len(valid_rates)
            else:
                best_rate = 0.0
            
        conn.close()
        return int(best_rate)
    except Exception as e:
        print(f"[ERROR] Database query failed: {e}")
        return None

@st.cache_data
def get_db_districts():
    db_paths = [
        os.path.join(os.path.dirname(__file__), "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "..", "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "..", "PythonProject1", "guidelines.db"),
        "guidelines.db",
        "PythonProject1/guidelines.db"
    ]
    db_path = None
    for p in db_paths:
        if os.path.exists(p):
            db_path = p
            break
    if not db_path:
        return []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT district FROM guidelines ORDER BY district")
        districts = [r[0] for r in cursor.fetchall() if r[0]]
        conn.close()
        return districts
    except Exception:
        return []

@st.cache_data
def get_db_taluks(district):
    db_paths = [
        os.path.join(os.path.dirname(__file__), "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "..", "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "..", "PythonProject1", "guidelines.db"),
        "guidelines.db",
        "PythonProject1/guidelines.db"
    ]
    db_path = None
    for p in db_paths:
        if os.path.exists(p):
            db_path = p
            break
    if not db_path:
        return []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT taluk_office FROM guidelines WHERE district = ? ORDER BY taluk_office", (district,))
        taluks = [r[0] for r in cursor.fetchall() if r[0]]
        conn.close()
        return taluks
    except Exception:
        return []

@st.cache_data
def get_db_villages(district, taluk):
    db_paths = [
        os.path.join(os.path.dirname(__file__), "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "..", "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "..", "PythonProject1", "guidelines.db"),
        "guidelines.db",
        "PythonProject1/guidelines.db"
    ]
    db_path = None
    for p in db_paths:
        if os.path.exists(p):
            db_path = p
            break
    if not db_path:
        return []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT village_area FROM guidelines WHERE district = ? AND taluk_office = ? ORDER BY village_area", (district, taluk))
        raw_villages = [r[0] for r in cursor.fetchall() if r[0]]
        conn.close()
        
        # Filter out survey-number-only descriptions to keep dropdowns clean
        import re
        filtered_villages = []
        for v in raw_villages:
            # If it is purely digits, dashes, spaces, slashes, commas, dots, and pipes, skip it!
            if re.match(r'^[\d\s\-\|.,/()\\\[\]]+$', v):
                continue
            filtered_villages.append(v)
            
        if not filtered_villages:
            return raw_villages
        return filtered_villages
    except Exception:
        return []

def get_property_rates(state, district, village, pincode, land_type, taluk=None, survey_number=None):
    # 1. Query Kaveri DB if state is Karnataka
    if state == "Karnataka":
        db_rate = lookup_db_guideline(district, taluk, village, land_type, survey_number=survey_number)
        if db_rate is not None:
            # Multiplier and growth rates fallback
            market_mult = 2.5 if land_type == "Residential" else (3.0 if land_type == "Commercial" else 1.5)
            growth_rate = 0.12 if land_type == "Residential" else (0.15 if land_type == "Commercial" else 0.06)
            return db_rate, market_mult, growth_rate

    # 2. Check GEO_DB
    if state and district:
        state_match = GEO_DB.get(state)
        if state_match:
            dist_match = state_match["districts"].get(district)
            if dist_match:
                base_guidance = dist_match["base_guidance"]
                market_mult = dist_match["market_multiplier"]
                growth_rate = dist_match["growth_rate"]
                
                # Apply area modifier for land type
                type_multipliers = {
                    "Residential": 1.0,
                    "Commercial": 1.5,
                    "Agricultural": 0.4,
                    "Industrial": 1.1
                }
                mult = type_multipliers.get(land_type or "Residential", 1.0)
                guidance = int(base_guidance * mult)
                return guidance, market_mult, growth_rate

    # 3. Fallback to hashing
    return get_hashed_rate(state or "", district or "", village or "", pincode or "", land_type or "Residential")

def calculate_valuation(state, district, village, pincode, survey_number, land_area, land_type, lat, lon,
                        property_class="Land only", built_up_area=0, building_age=0, construction_quality="Standard",
                        land_price=0.0, taluk=None):
    print("Starting property valuation process...")
    
    # Input validation checks
    if not state or state == "Select State" or not state.strip():
        raise ValueError("State name is missing or invalid.")
    if not district or district == "Select District" or not district.strip():
        raise ValueError("District name is missing or invalid.")
    if not village or not village.strip():
        raise ValueError("Village/Layout name is missing.")
    if not survey_number or not survey_number.strip():
        raise ValueError("Survey/Khata number is missing.")
    if land_area is None:
        raise ValueError("Land area must be specified.")
    if land_area <= 0:
        raise ValueError("Land area must be a positive number greater than 0.")
    if not land_type or not land_type.strip():
        raise ValueError("Land type must be specified (e.g. Residential, Commercial).")
    if lat is None or lon is None:
        raise ValueError("Latitude and Longitude coordinates must be pinned.")

    print(f"Reading property details: State={state}, District={district}, Village={village}, Land Area={land_area} sqft, Type={land_type}")
    
    # Lookup guidance rates
    print("Looking up guidance rates and market multiplier indices...")
    guidance_per_sqft, market_mult, growth_rate = get_property_rates(state, district, village, pincode, land_type, taluk=taluk, survey_number=survey_number)
    print(f"Guidance rate found: Rs. {guidance_per_sqft}/sqft, Multiplier: {market_mult}, Projected growth: {growth_rate*100}%")
    
    # Use ML model if exists, otherwise fallback to mathematical formulation
    market_per_sqft = int(guidance_per_sqft * market_mult)
    
    print("Loading valuation model...")
    from utils.model_loader import get_valuation_model
    val_model = get_valuation_model()
    if val_model is not None:
        try:
                
            input_df = pd.DataFrame([{
                "State": state,
                "District": district,
                "Land_Type": land_type,
                "Land_Area": land_area,
                "Guidance_Value_Per_Sqft": guidance_per_sqft
            }])
            print(f"Model inputs prepared: {input_df.to_dict(orient='records')[0]}")
            print(f"Model columns count: {len(input_df.columns)}, Names: {list(input_df.columns)}")
            
            # Explicit column validation check
            expected_cols = ["State", "District", "Land_Type", "Land_Area", "Guidance_Value_Per_Sqft"]
            missing_cols = [col for col in expected_cols if col not in input_df.columns]
            if missing_cols:
                raise ValueError(f"Model input schema error. Missing columns: {missing_cols}")
                
            predicted_rate = val_model.predict(input_df)[0]
            market_per_sqft = int(predicted_rate)
            print("Model prediction completed.")
        except Exception as e:
            print("Error loading ML valuation model, using formula. Error:", e)
    else:
        print("Valuation model .pkl file not found on server, using fallback guidance formula.")
            
    # Apply land price override logic if specified
    if land_price > 0:
        if land_price < 60000:
            market_per_sqft = int(land_price)
            land_market_value = int(market_per_sqft * land_area)
        else:
            land_market_value = int(land_price)
            market_per_sqft = int(land_price / land_area) if land_area > 0 else 0
    else:
        land_market_value = market_per_sqft * land_area
    
    # Home / Building Valuation
    building_market_value = 0
    building_guidance_value = 0
    construction_cost_sqft = 0
    depreciated_factor = 1.0
    
    if property_class != "Land only" and built_up_area > 0:
        construction_rates = {
            "Standard": 1600,
            "Premium": 2400,
            "Luxury": 3600
        }
        guidance_rates = {
            "Standard": 1000,
            "Premium": 1500,
            "Luxury": 2200
        }
        construction_cost_sqft = construction_rates.get(construction_quality, 1600)
        # 1.5% annual depreciation, capped at 75% max depreciation (25% residual value)
        depreciated_factor = max(0.25, 1.0 - (building_age * 0.015))
        building_market_value = int(built_up_area * construction_cost_sqft * depreciated_factor)
        building_guidance_value = int(built_up_area * guidance_rates.get(construction_quality, 1000))
        
    total_market_value = land_market_value + building_market_value
    total_guidance_value = int(guidance_per_sqft * land_area) + building_guidance_value
    
    # Nearby averages
    nearby_1 = int(market_per_sqft * 0.95)
    nearby_2 = int(market_per_sqft * 1.08)
    nearby_3 = int(market_per_sqft * 0.91)
    avg_nearby = int((nearby_1 + nearby_2 + nearby_3) / 3)
    
    # Growth projections
    proj_1yr = int(total_market_value * (1 + growth_rate))
    proj_3yr = int(total_market_value * (1 + growth_rate)**3)
    proj_5yr = int(total_market_value * (1 + growth_rate)**5)
    
    # Fraud indicators
    fraud_flags = []
    fraud_level = "PASS"
    
    # A. Geographic coordinate check (India bounding box roughly: lat 8 to 38, lon 68 to 97)
    if not (8.0 <= lat <= 38.0 and 68.0 <= lon <= 97.0):
        fraud_flags.append("Warning: Coordinates are outside the borders of India.")
        fraud_level = "WARNING"
    
    # B. Circle/Market divergence
    if total_guidance_value > total_market_value * 1.3:
        fraud_flags.append("High Risk: Government guidance value significantly exceeds estimated market rate.")
        fraud_level = "HIGH RISK"
    elif total_market_value > total_guidance_value * 5:
        # Abnormally high premium
        fraud_flags.append("Warning: Market value is over 5x the Government guidance rate (Speculative pricing).")
        if fraud_level != "HIGH RISK":
            fraud_level = "WARNING"
            
    # C. Area checks
    if land_area <= 100:
        fraud_flags.append("Warning: Extravagantly small land plot area.")
        if fraud_level != "HIGH RISK":
            fraud_level = "WARNING"

    # LTV guidelines
    ltv_limits = {
        "Residential": 0.80,
        "Commercial": 0.75,
        "Agricultural": 0.60,
        "Industrial": 0.70
    }
    eligible_ltv = ltv_limits.get(land_type, 0.70)
    max_loan_amount = int(total_market_value * eligible_ltv)
    print(f"Property valuation completed successfully. Market value: Rs. {total_market_value}, Guidance value: Rs. {total_guidance_value}")
    return {
        "guidance_value_per_sqft": guidance_per_sqft,
        "total_guidance_value": total_guidance_value,
        "market_value_per_sqft": market_per_sqft,
        "total_market_value": total_market_value,
        "nearby_prices": [nearby_1, nearby_2, nearby_3],
        "avg_nearby_value_per_sqft": avg_nearby,
        "projections": {
            "1yr": proj_1yr,
            "3yr": proj_3yr,
            "5yr": proj_5yr,
            "growth_rate_pct": int(growth_rate * 100)
        },
        "fraud_check": {
            "status": fraud_level,
            "flags": fraud_flags
        },
        "eligible_ltv": eligible_ltv,
        "max_loan_amount": max_loan_amount,
        # Home valuation details
        "property_class": property_class,
        "built_up_area": built_up_area,
        "building_age": building_age,
        "construction_quality": construction_quality,
        "land_market_value": land_market_value,
        "building_market_value": building_market_value,
        "building_guidance_value": building_guidance_value,
        "construction_cost_sqft": construction_cost_sqft,
        "depreciated_factor": depreciated_factor
    }

@st.cache_data
def geocode_address(state, district, taluk=None, village=None):
    import requests
    import re
    
    karnataka_coords = {
        "Bagalkote": [16.1813, 75.6961],
        "Bangalore Rural": [13.2925, 77.5500],
        "Bangalore Urban": [12.9716, 77.5946],
        "Belagavi": [15.8497, 74.4977],
        "Bellary": [15.1394, 76.9214],
        "Bidar": [17.9104, 77.5199],
        "Chamarajanagar": [11.9261, 76.9402],
        "Chikkaballapura": [13.4354, 77.7277],
        "Chikkamagalur": [13.3161, 75.7720],
        "Chitradurga": [14.2300, 76.4000],
        "Davangere": [14.4644, 75.9218],
        "Dharwad": [15.4589, 75.0078],
        "Gadag": [15.4267, 75.6267],
        "Gulbarga": [17.3291, 76.8341],
        "Hassan": [13.0072, 76.1026],
        "Haveri": [14.7954, 75.3995],
        "Karwar": [14.8093, 74.1300],
        "Kodagu": [12.2681, 75.7381],
        "Kolar": [13.1373, 78.1345],
        "Koppal": [15.3484, 76.1554],
        "Mandya": [12.5218, 76.8951],
        "Mangalore": [12.9141, 74.8560],
        "Mysore": [12.2958, 76.6394],
        "Raichur": [16.2120, 77.3550],
        "Ramanagara": [12.7150, 77.2813],
        "Shimoga": [13.9299, 75.5681],
        "Tumkur": [13.3379, 77.1173],
        "Udupi": [13.3409, 74.7421],
        "Vijayapura": [16.8302, 75.7100],
        "Yadagiri": [16.7667, 77.1333]
    }
    
    fallback_coord = [12.9716, 77.5946] # Bengaluru default
    if state == "Karnataka":
        for k_dist, k_coords in karnataka_coords.items():
            if district and (district.lower() in k_dist.lower() or k_dist.lower() in district.lower()):
                fallback_coord = k_coords
                break
                
    if not district or not state:
        return fallback_coord
        
    if village or taluk:
        clean_village = ""
        if village:
            parts = village.split("|")
            clean_village = parts[-1].strip() if parts else village
            clean_village = re.sub(r'[\d/\-]', '', clean_village).strip()
            
        search_query = f"{clean_village or taluk or ''}, {district}, {state}, India"
        try:
            headers = {"User-Agent": "AegisCR-Valuation-App/1.0"}
            url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(search_query)}&format=json&limit=1"
            r = requests.get(url, headers=headers, timeout=2)
            if r.status_code == 200 and r.json():
                data = r.json()[0]
                return float(data["lat"]), float(data["lon"])
        except Exception:
            pass
            
    return fallback_coord
