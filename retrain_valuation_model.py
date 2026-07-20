import pandas as pd
import numpy as np
import pickle
import random
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

def map_land_type(classification):
    c = str(classification).lower()
    if "commercial" in c or "shop" in c or "office" in c:
        return "Commercial"
    elif "industrial" in c or "factory" in c or "shed" in c:
        return "Industrial"
    elif "site" in c or "apartment" in c or "flat" in c or "residential" in c or "house" in c or "building" in c or "gramathana" in c:
        return "Residential"
    else:
        return "Agricultural"

def get_market_multiplier(district, land_type):
    d = str(district).lower()
    t = str(land_type).lower()
    
    # Base multiplier based on district prominence
    if "bengaluru" in d or "bangalore" in d or "basavanagudi" in d or "gandhinagar" in d or "jayanagar" in d or "rajajinagar" in d or "shivajinagar" in d:
        base = 2.5
    elif "mysore" in d or "mysuru" in d or "mangalore" in d or "mangaluru" in d:
        base = 1.8
    elif "dharwad" in d or "belagavi" in d or "tumkur" in d or "udupi" in d:
        base = 1.5
    else:
        base = 1.3
        
    # Adjustment by land type
    if t == "commercial":
        return base * 1.3
    elif t == "residential":
        return base * 1.1
    elif t == "industrial":
        return base * 1.0
    else: # agricultural
        return base * 0.9

def retrain():
    csv_path = r"C:\Users\shash\OneDrive\Desktop\guidelines_pdfs (1)\guidelines_sqft_valuation.csv"
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return
        
    print("Loading circular rates CSV dataset...")
    df = pd.read_csv(csv_path)
    print("Total raw records loaded:", len(df))
    
    # Drop rows with missing rate
    df = df.dropna(subset=["Rate_Per_Sqft"])
    df = df[df["Rate_Per_Sqft"] > 0]
    print("Records with positive sqft rate:", len(df))
    
    # Sample 80,000 records to keep training fast and memory usage efficient
    sample_size = min(80000, len(df))
    df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
    print("Sampled records for training:", len(df))
    
    # 1. Map features
    df["State"] = "Karnataka"
    df["District"] = df["District"].str.title()
    df["Land_Type"] = df["Property_Classification"].apply(map_land_type)
    df["Guidance_Value_Per_Sqft"] = df["Rate_Per_Sqft"]
    
    # 2. Simulate Land Area based on classification
    def sim_area(land_type):
        if land_type == "Agricultural":
            return random.randint(10000, 87120)
        elif land_type == "Industrial":
            return random.randint(5000, 45000)
        elif land_type == "Commercial":
            return random.randint(1000, 12000)
        else: # Residential
            return random.choice([1200, 2400, 4000, 1500, 3000])
            
    df["Land_Area"] = df["Land_Type"].apply(sim_area)
    
    # 3. Calculate target Market_Value_Per_Sqft
    def calc_market_value(row):
        mult = get_market_multiplier(row["District"], row["Land_Type"])
        # Add random noise between -10% and +15%
        noise = random.uniform(-0.10, 0.15)
        return round(row["Guidance_Value_Per_Sqft"] * mult * (1.0 + noise), 2)
        
    df["Market_Value_Per_Sqft"] = df.apply(calc_market_value, axis=1)
    
    # 4. Train regression model
    features = ["State", "District", "Land_Type", "Land_Area", "Guidance_Value_Per_Sqft"]
    X = df[features]
    y = df["Market_Value_Per_Sqft"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Preprocessor
    cat_cols = ["State", "District", "Land_Type"]
    num_cols = ["Land_Area", "Guidance_Value_Per_Sqft"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", StandardScaler(), num_cols)
        ]
    )
    
    # Pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=60, max_depth=12, min_samples_leaf=3, random_state=42, n_jobs=-1))
    ])
    
    print("Fitting Random Forest model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    preds = pipeline.predict(X_test)
    r2 = r2_score(y_test, preds)
    print(f"\nRetrained Model Valuation R2 Score: {r2:.4f}")
    
    # Save model in both directory configurations to guarantee loading compatibility
    paths = [
        "valuation_model.pkl",
        os.path.join("PythonProject1", "valuation_model.pkl")
    ]
    for p in paths:
        try:
            with open(p, "wb") as f:
                pickle.dump(pipeline, f)
            print("Successfully written pickled model to:", p)
        except Exception as e:
            print("Could not write to path:", p, "-", str(e))
            
if __name__ == "__main__":
    retrain()
