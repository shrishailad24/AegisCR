import os
import pickle
import hashlib
import pandas as pd
import numpy as np

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

def get_property_rates(state, district, village, pincode, land_type):
    # 1. Check GEO_DB
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
            mult = type_multipliers.get(land_type, 1.0)
            guidance = int(base_guidance * mult)
            return guidance, market_mult, growth_rate

    # 2. Fallback to hashing
    return get_hashed_rate(state, district, village, pincode, land_type)

def calculate_valuation(state, district, village, pincode, survey_number, land_area, land_type, lat, lon,
                        property_class="Land only", built_up_area=0, building_age=0, construction_quality="Standard"):
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
    if land_area is None or land_area <= 0:
        raise ValueError("Land area must be a positive number greater than 0.")
    if not land_type or not land_type.strip():
        raise ValueError("Land type must be specified (e.g. Residential, Commercial).")
    if lat is None or lon is None:
        raise ValueError("Latitude and Longitude coordinates must be pinned.")

    print(f"Reading property details: State={state}, District={district}, Village={village}, Land Area={land_area} sqft, Type={land_type}")
    
    # Lookup guidance rates
    print("Looking up guidance rates and market multiplier indices...")
    guidance_per_sqft, market_mult, growth_rate = get_property_rates(state, district, village, pincode, land_type)
    print(f"Guidance rate found: ₹{guidance_per_sqft}/sqft, Multiplier: {market_mult}, Projected growth: {growth_rate*100}%")
    
    # Use ML model if exists, otherwise fallback to mathematical formulation
    market_per_sqft = int(guidance_per_sqft * market_mult)
    
    print("Loading valuation model...")
    if os.path.exists("valuation_model.pkl"):
        try:
            with open("valuation_model.pkl", "rb") as f:
                val_model = pickle.load(f)
            print("Valuation model loaded successfully.")
                
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
    print(f"Property valuation completed successfully. Market value: ₹{total_market_value}, Guidance value: ₹{total_guidance_value}")
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
