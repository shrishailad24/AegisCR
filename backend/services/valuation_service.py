import pandas as pd
from utils.model_loader import get_valuation_model

def evaluate_property_value(state, district, taluk, village, latitude, longitude, area, guidance_value, property_type):
    val_model = get_valuation_model()
    predicted_rate = None
    
    if val_model is not None:
        try:
            input_df = pd.DataFrame([{
                "State": state,
                "District": district,
                "Land_Type": property_type,
                "Land_Area": area,
                "Guidance_Value_Per_Sqft": guidance_value
            }])
            predicted_rate = float(val_model.predict(input_df)[0])
        except Exception as e:
            print(f"[API ML PREDICTION SERVICE ERROR] {e}")
            
    if predicted_rate is None:
        # Fallback formulation
        mult = 2.5
        p_type = property_type.lower()
        if "commercial" in p_type:
            mult = 3.0
        elif "agricultural" in p_type or "dry" in p_type or "soil" in p_type:
            mult = 1.5
        elif "industrial" in p_type:
            mult = 2.8
        predicted_rate = guidance_value * mult
        
    predicted_value = int(predicted_rate * area)
    
    # Calculate dynamic confidence
    confidence = 92.0
    if not (11.5 <= latitude <= 18.5 and 74.0 <= longitude <= 78.5):
        confidence -= 10.0
    if guidance_value <= 0:
        confidence -= 15.0
    confidence = max(50.0, min(98.0, confidence))
    
    # Calculate dynamic investment score
    growth_potential = 0.05
    p_type = property_type.lower()
    if "commercial" in p_type:
        growth_potential = 0.08
    elif "residential" in p_type:
        growth_potential = 0.06
    elif "industrial" in p_type:
        growth_potential = 0.07
        
    premium_ratio = predicted_rate / (guidance_value or 1.0)
    score = 6.0 + (growth_potential * 20.0) + (premium_ratio * 0.5)
    investment_score = round(max(1.0, min(10.0, score)), 1)
    
    import gc
    gc.collect() # Release memory buffers after ML prediction
    
    return {
        "predicted_value": predicted_value,
        "confidence": int(confidence),
        "investment_score": investment_score,
        "rate_per_sqft": round(predicted_rate, 2)
    }
