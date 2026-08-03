from backend.database.db import get_db_connection
from fastapi import HTTPException
from functools import lru_cache

@lru_cache(maxsize=128)
def fetch_districts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT district FROM guidelines ORDER BY district")
    rows = cursor.fetchall()
    districts = [row["district"] for row in rows if row["district"]]
    conn.close()
    return districts

@lru_cache(maxsize=256)
def fetch_taluks(district: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT taluk_office FROM guidelines WHERE district = ? ORDER BY taluk_office", (district,))
    rows = cursor.fetchall()
    taluks = [row["taluk_office"] for row in rows if row["taluk_office"]]
    conn.close()
    return taluks

@lru_cache(maxsize=512)
def fetch_villages(district: str, taluk: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT village_area FROM guidelines WHERE district = ? AND taluk_office = ? ORDER BY village_area",
        (district, taluk)
    )
    rows = cursor.fetchall()
    villages = [row["village_area"] for row in rows if row["village_area"]]
    conn.close()
    return villages

def fetch_guideline_rate(district: str, taluk: str, village: str, land_type: str, state: str):
    if state != "Karnataka":
        # Modular support for other states - returns mock/template rates
        mock_records = [
            {
                "district": district,
                "taluk": taluk,
                "village": village,
                "property_type": "Standard Residential (Mock)",
                "guidance_value": 1500.0,
                "rate_per_sqft": 1500.0,
                "rate_per_acre": 1500.0 * 43560.0,
                "original_unit": "Sq Ft",
                "locality": f"{village}, {taluk} ({state})"
            },
            {
                "district": district,
                "taluk": taluk,
                "village": village,
                "property_type": "Standard Agricultural (Mock)",
                "guidance_value": 500000.0,
                "rate_per_sqft": 11.48,
                "rate_per_acre": 500000.0,
                "original_unit": "Acre",
                "locality": f"{village}, {taluk} ({state})"
            }
        ]
        best_rate = 1500.0 if land_type == "Residential" else 11.48
        matched_class = "Standard Residential (Mock)" if land_type == "Residential" else "Standard Agricultural (Mock)"
        return {
            "state": state,
            "district": district,
            "taluk": taluk,
            "village": village,
            "land_type": land_type,
            "matched_classification": matched_class,
            "guideline_rate_per_sqft": best_rate,
            "unit": "₹/sqft",
            "records": mock_records
        }

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Precise lookup query
    cursor.execute("""
        SELECT district, taluk_office, village_area, property_classification, original_rate, original_unit, rate_per_sqft, unit
        FROM guidelines
        WHERE (district LIKE ? OR taluk_office LIKE ?) AND taluk_office LIKE ? AND village_area LIKE ?
    """, (f"%{district}%", f"%{district}%", f"%{taluk}%", f"%{village}%"))
    
    rows = cursor.fetchall()
    
    # Fallback to village only
    if not rows:
        cursor.execute("""
            SELECT district, taluk_office, village_area, property_classification, original_rate, original_unit, rate_per_sqft, unit
            FROM guidelines
            WHERE (district LIKE ? OR taluk_office LIKE ?) AND village_area LIKE ?
        """, (f"%{district}%", f"%{district}%", f"%{village}%"))
        rows = cursor.fetchall()
        
    # Fallback to taluk average
    if not rows:
        cursor.execute("""
            SELECT district, taluk_office, village_area, property_classification, original_rate, original_unit, rate_per_sqft, unit
            FROM guidelines
            WHERE district LIKE ? OR taluk_office LIKE ?
        """, (f"%{district}%", f"%{district}%"))
        rows = cursor.fetchall()
        
    if not rows:
        conn.close()
        return {
            "state": state,
            "district": district,
            "taluk": taluk,
            "village": village,
            "land_type": land_type,
            "matched_classification": "No guidance value available",
            "guideline_rate_per_sqft": 0.0,
            "unit": "₹/sqft",
            "records": []
        }
        
    best_rate = None
    matched_class = "Fallback / Average"
    l_type_lower = land_type.lower()

    for row in rows:
        rate = row["rate_per_sqft"]
        classification = row["property_classification"]
        if not classification:
            continue
        cls_lower = classification.lower()
        
        # Exact classification matching for specific land types
        if l_type_lower in ["dry land", "dry"] and "dry land" in cls_lower and "black" not in cls_lower:
            best_rate = rate
            matched_class = classification
            break
        elif l_type_lower in ["black soil dry", "black soil"] and "black soil" in cls_lower:
            best_rate = rate
            matched_class = classification
            break
        elif l_type_lower in ["wet land", "wet"] and "wet land" in cls_lower:
            best_rate = rate
            matched_class = classification
            break
        elif l_type_lower in ["bagayat land", "bagayat"] and "bagayat" in cls_lower:
            best_rate = rate
            matched_class = classification
            break
        elif "agricultural" in l_type_lower and any(k in cls_lower for k in ["dry", "soil", "wet", "bagayat"]):
            best_rate = rate
            matched_class = classification
            break
        elif ("commercial" in l_type_lower or "shop" in l_type_lower) and any(k in cls_lower for k in ["commercial", "site", "approved"]):
            best_rate = rate * (1.5 if "commercial" not in cls_lower else 1.0)
            matched_class = classification
            break
        elif any(k in l_type_lower for k in ["residential", "home", "apartment", "site"]) and any(k in cls_lower for k in ["residential", "gramathana", "approved", "site"]):
            best_rate = rate
            matched_class = classification
            break
            
    if best_rate is None:
        rates = [r["rate_per_sqft"] for r in rows if r["rate_per_sqft"] is not None]
        best_rate = sum(rates) / len(rates) if rates else 0.0
        
    # Compile all records
    records = []
    for r in rows:
        orig_rate = r["original_rate"] if r["original_rate"] is not None else (r["rate_per_sqft"] or 0.0)
        orig_unit = r["original_unit"] or "Sq Ft"
        
        # rate per acre calculation
        rate_ac = None
        if orig_unit and "acre" in orig_unit.lower():
            rate_ac = orig_rate
        elif r["rate_per_sqft"] is not None:
            rate_ac = r["rate_per_sqft"] * 43560.0
            
        records.append({
            "district": r["district"],
            "taluk": r["taluk_office"],
            "village": r["village_area"],
            "property_type": r["property_classification"],
            "guidance_value": orig_rate,
            "rate_per_sqft": r["rate_per_sqft"] or 0.0,
            "rate_per_acre": round(rate_ac, 2) if rate_ac is not None else None,
            "original_unit": orig_unit,
            "locality": f"{r['village_area']}, {r['taluk_office']}"
        })
        
    conn.close()
    return {
        "state": state,
        "district": district,
        "taluk": taluk,
        "village": village,
        "land_type": land_type,
        "matched_classification": matched_class,
        "guideline_rate_per_sqft": round(best_rate, 4),
        "unit": "₹/sqft",
        "records": records
    }
