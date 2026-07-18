from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI(
    title="Kaveri Land Valuation Guideline API",
    description="API to query Karnataka standardized land circle rates (₹/sqft)",
    version="1.0.0"
)

# Enable CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    db_paths = [
        os.path.join(os.path.dirname(__file__), "..", "PythonProject1", "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "guidelines.db"),
        os.path.join(os.path.dirname(__file__), "..", "guidelines.db"),
        "guidelines.db",
        "PythonProject1/guidelines.db"
    ]
    for p in db_paths:
        if os.path.exists(p):
            conn = sqlite3.connect(p)
            conn.row_factory = sqlite3.Row
            return conn
    raise HTTPException(status_code=500, detail="guidelines.db SQLite database not found on backend server.")

@app.get("/api/districts")
def get_districts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT district FROM guidelines ORDER BY district")
        rows = cursor.fetchall()
        districts = [row["district"] for row in rows if row["district"]]
        conn.close()
        return {"districts": districts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/taluks")
def get_taluks(district: str = Query(..., description="District name")):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT taluk_office FROM guidelines WHERE district = ? ORDER BY taluk_office", (district,))
        rows = cursor.fetchall()
        taluks = [row["taluk_office"] for row in rows if row["taluk_office"]]
        conn.close()
        return {"taluks": taluks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/villages")
def get_villages(
    district: str = Query(..., description="District name"),
    taluk: str = Query(..., description="Taluk name / Sub-Registrar office")
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT village_area FROM guidelines WHERE district = ? AND taluk_office = ? ORDER BY village_area",
            (district, taluk)
        )
        rows = cursor.fetchall()
        villages = [row["village_area"] for row in rows if row["village_area"]]
        conn.close()
        return {"villages": villages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/guideline")
def get_guideline_rate(
    district: str = Query(..., description="District name"),
    taluk: str = Query(..., description="Taluk name"),
    village: str = Query(..., description="Village / area name"),
    land_type: str = Query("Residential", description="Residential, Commercial, Agricultural, Industrial")
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Precise lookup query
        cursor.execute("""
            SELECT rate_per_sqft, property_classification, original_unit
            FROM guidelines
            WHERE (district LIKE ? OR taluk_office LIKE ?) AND taluk_office LIKE ? AND village_area LIKE ?
        """, (f"%{district}%", f"%{district}%", f"%{taluk}%", f"%{village}%"))
        
        rows = cursor.fetchall()
        
        # Fallback to village only
        if not rows:
            cursor.execute("""
                SELECT rate_per_sqft, property_classification, original_unit
                FROM guidelines
                WHERE (district LIKE ? OR taluk_office LIKE ?) AND village_area LIKE ?
            """, (f"%{district}%", f"%{district}%", f"%{village}%"))
            rows = cursor.fetchall()
            
        # Fallback to taluk average
        if not rows:
            cursor.execute("""
                SELECT rate_per_sqft, property_classification, original_unit
                FROM guidelines
                WHERE district LIKE ? OR taluk_office LIKE ?
            """, (f"%{district}%", f"%{district}%"))
            rows = cursor.fetchall()
            
        if not rows:
            conn.close()
            raise HTTPException(status_code=404, detail="No matching guideline rates found for specified location.")
            
        best_rate = None
        matched_class = "Fallback / Average"
        for row in rows:
            rate = row["rate_per_sqft"]
            classification = row["property_classification"]
            cls_lower = classification.lower()
            
            if land_type == "Agricultural" and any(k in cls_lower for k in ["dry", "soil", "wet", "bagayat"]):
                best_rate = rate
                matched_class = classification
                break
            elif land_type == "Residential" and any(k in cls_lower for k in ["residential", "gramathana", "approved", "site"]):
                best_rate = rate
                matched_class = classification
                break
            elif land_type == "Commercial" and any(k in cls_lower for k in ["commercial", "approved", "residential", "site"]):
                best_rate = rate * 1.5
                matched_class = f"{classification} (Commercial 1.5x Multiplier)"
                break
            elif land_type == "Industrial" and any(k in cls_lower for k in ["industrial", "approved", "residential", "site"]):
                best_rate = rate * 1.1
                matched_class = f"{classification} (Industrial 1.1x Multiplier)"
                break
                
        if best_rate is None:
            rates = [r["rate_per_sqft"] for r in rows]
            best_rate = sum(rates) / len(rates)
            
        conn.close()
        return {
            "district": district,
            "taluk": taluk,
            "village": village,
            "land_type": land_type,
            "matched_classification": matched_class,
            "guideline_rate_per_sqft": round(best_rate, 4),
            "unit": "₹/sqft"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
