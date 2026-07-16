import pandas as pd
import numpy as np
import random
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Define geographical data dictionary for Indian states
geo_data = {
    "Karnataka": {
        "districts": {
            "Bengaluru Urban": {
                "villages": ["Whitefield", "Electronic City", "Kengeri", "Yelahanka", "Sarjapur"],
                "base_guidance": 3500, # per sqft
                "market_multiplier": 2.5
            },
            "Mysuru": {
                "villages": ["Gokulam", "Vijayanagar", "J P Nagar", "Hebbal", "Ramakrishnanagar"],
                "base_guidance": 1800,
                "market_multiplier": 1.8
            },
            "Dharwad": {
                "villages": ["Navanagar", "Sattur", "Vidyagiri", "Lakamanahalli", "Kelageri"],
                "base_guidance": 1200,
                "market_multiplier": 1.5
            }
        },
        "pincodes": {
            "Bengaluru Urban": ["560066", "560100", "560060", "560064", "560035"],
            "Mysuru": ["570002", "570017", "570008", "570016", "570020"],
            "Dharwad": ["580025", "580009", "580004", "580008", "580007"]
        }
    },
    "Telangana": {
        "districts": {
            "Hyderabad": {
                "villages": ["Gachibowli", "Madhapur", "Jubilee Hills", "Banjara Hills", "Kondapur"],
                "base_guidance": 5000,
                "market_multiplier": 3.0
            },
            "Medchal-Malkajgiri": {
                "villages": ["Kompally", "Malkajgiri", "Medchal", "Alwal", "Medipally"],
                "base_guidance": 2200,
                "market_multiplier": 2.0
            },
            "Rangareddy": {
                "villages": ["Gandi Maisamma", "Narsingi", "Kokapet", "Puppalguda", "Rajendranagar"],
                "base_guidance": 3000,
                "market_multiplier": 2.3
            }
        },
        "pincodes": {
            "Hyderabad": ["500032", "500081", "500033", "500034", "500084"],
            "Medchal-Malkajgiri": ["500014", "500047", "501401", "500010", "500098"],
            "Rangareddy": ["500043", "500075", "500089", "500090", "500030"]
        }
    },
    "Maharashtra": {
        "districts": {
            "Mumbai Suburban": {
                "villages": ["Andheri", "Bandra", "Borivali", "Kurla", "Ghatkopar"],
                "base_guidance": 8000,
                "market_multiplier": 3.5
            },
            "Pune": {
                "villages": ["Hinjawadi", "Hadapsar", "Baner", "Kothrud", "Wakad"],
                "base_guidance": 3200,
                "market_multiplier": 2.2
            },
            "Nagpur": {
                "villages": ["Dharampeth", "Manish Nagar", "Somalwada", "Wardha Road", "Sitabuldi"],
                "base_guidance": 1500,
                "market_multiplier": 1.6
            }
        },
        "pincodes": {
            "Mumbai Suburban": ["400053", "400050", "400092", "400070", "400086"],
            "Pune": ["411057", "411028", "411045", "411038", "411057"],
            "Nagpur": ["440010", "440015", "440025", "440015", "440012"]
        }
    },
    "Tamil Nadu": {
        "districts": {
            "Chennai": {
                "villages": ["Adyar", "Velachery", "Mylapore", "Tambaram", "Guindy"],
                "base_guidance": 4500,
                "market_multiplier": 2.8
            },
            "Coimbatore": {
                "villages": ["Peelamedu", "Gandhipuram", "R S Puram", "Saravanampatti", "Singanallur"],
                "base_guidance": 2000,
                "market_multiplier": 1.9
            },
            "Madurai": {
                "villages": ["Anna Nagar", "K K Nagar", "Othakadai", "Sellur", "Tallakulam"],
                "base_guidance": 1300,
                "market_multiplier": 1.5
            }
        },
        "pincodes": {
            "Chennai": ["600020", "600042", "600004", "600045", "600032"],
            "Coimbatore": ["641004", "641012", "641002", "641035", "641005"],
            "Madurai": ["625020", "625020", "625107", "625002", "625002"]
        }
    }
}

def generate_records(num_records=12000):
    records = []
    
    states = list(geo_data.keys())
    land_types = ["Residential", "Commercial", "Agricultural", "Industrial"]
    genders = ["Male", "Female"]
    married_options = ["Yes", "No"]
    education_options = ["Graduate", "Not Graduate"]
    self_emp_options = ["Yes", "No"]
    
    for i in range(num_records):
        state = random.choice(states)
        district = random.choice(list(geo_data[state]["districts"].keys()))
        
        # Get matching village and pincode index
        village_list = geo_data[state]["districts"][district]["villages"]
        pincode_list = geo_data[state]["pincodes"][district]
        
        idx = random.randint(0, len(village_list) - 1)
        village = village_list[idx]
        pincode = pincode_list[idx]
        
        # Add survey number (format: 100-200 / subnumber)
        survey_number = f"{random.randint(1, 500)}/{random.randint(1, 10)}"
        
        # Land characteristics
        land_type = random.choice(land_types)
        
        # Base dimensions (sqft)
        if land_type == "Agricultural":
            # Typically larger, let's say 10000 to 100000 sqft (roughly 0.25 to 2.3 acres)
            land_area = random.randint(10000, 100000)
            area_multiplier = 0.4 # Agricultural land guidance is lower per sqft
        elif land_type == "Industrial":
            land_area = random.randint(5000, 50000)
            area_multiplier = 1.1
        elif land_type == "Commercial":
            land_area = random.randint(1000, 15000)
            area_multiplier = 1.5
        else: # Residential
            land_area = random.randint(800, 8000)
            area_multiplier = 1.0
            
        base_guidance = geo_data[state]["districts"][district]["base_guidance"]
        market_multiplier = geo_data[state]["districts"][district]["market_multiplier"]
        
        # Calculate guidance value per sqft with some random variation
        guidance_per_sqft = int(base_guidance * area_multiplier * random.uniform(0.85, 1.15))
        total_guidance_value = int(guidance_per_sqft * land_area)
        
        # Market value per sqft
        market_per_sqft = int(guidance_per_sqft * market_multiplier * random.uniform(1.1, 1.5))
        total_market_value = int(market_per_sqft * land_area)
        
        # Nearby property prices simulation (average of 3 properties nearby)
        nearby_price_1 = int(market_per_sqft * random.uniform(0.9, 1.1))
        nearby_price_2 = int(market_per_sqft * random.uniform(0.85, 1.15))
        nearby_price_3 = int(market_per_sqft * random.uniform(0.95, 1.05))
        avg_nearby_price_per_sqft = int((nearby_price_1 + nearby_price_2 + nearby_price_3) / 3)
        total_nearby_avg_value = avg_nearby_price_per_sqft * land_area
        
        # Applicant details
        gender = random.choice(genders)
        married = random.choice(married_options)
        dependents = random.choice([0, 1, 2, 3])
        education = random.choice(education_options)
        self_employed = random.choice(self_emp_options)
        
        # Incomes (in Rs)
        app_income = int(np.random.lognormal(mean=10.5, sigma=0.6))  # typical range 15k to 150k
        app_income = max(12000, min(app_income, 450000))
        
        co_income = 0
        if random.random() > 0.4:
            co_income = int(np.random.lognormal(mean=10.0, sigma=0.6))
            co_income = max(8000, min(co_income, 250000))
            
        total_income = app_income + co_income
        
        # Credit history (1.0 or 0.0)
        credit_history = 1.0 if random.random() < 0.82 else 0.0
        
        # Property Area setting
        if land_type == "Agricultural":
            property_area = "Rural"
        elif district in ["Bengaluru Urban", "Hyderabad", "Mumbai Suburban", "Chennai"]:
            property_area = "Urban" if random.random() < 0.85 else "Semiurban"
        else:
            property_area = "Semiurban" if random.random() < 0.70 else "Rural"
            
        # Requested Loan Amount (usually based on property value)
        # Banks fund 50% to 80% of market value
        ltv_ratio_requested = random.uniform(0.3, 0.95)
        loan_amount = int(total_market_value * ltv_ratio_requested)
        
        # Term in months
        loan_term = random.choice([120, 180, 240, 300, 360])
        
        # Calculate EMI roughly at 9% annual interest
        monthly_interest = 0.09 / 12
        emi = loan_amount * (monthly_interest * (1 + monthly_interest)**loan_term) / ((1 + monthly_interest)**loan_term - 1)
        
        approval_prob = 0.85
        
        # Rule checks
        if credit_history == 0.0:
            approval_prob -= 0.75
            
        actual_ltv = loan_amount / total_market_value
        if land_type == "Agricultural" and actual_ltv > 0.65:
            approval_prob -= 0.3
        elif actual_ltv > 0.80:
            approval_prob -= 0.25
        if actual_ltv > 0.95:
            approval_prob -= 0.4
            
        dti = emi / total_income
        if dti > 0.50:
            approval_prob -= 0.35
        elif dti > 0.40:
            approval_prob -= 0.15
            
        # Make a baseline threshold for approval
        loan_approved = 1 if (random.random() < approval_prob and approval_prob > 0.15) else 0
        
        # Risk Score (0 to 100, where higher is riskier)
        risk_score = 0
        if credit_history == 0.0:
            risk_score += 40
        risk_score += int(min(actual_ltv * 40, 40))
        risk_score += int(min(dti * 30, 20))
        if land_type == "Agricultural":
            risk_score += 10
        risk_score = min(max(risk_score, 5), 98) # Keep within 5-98 range
        
        records.append({
            "State": state,
            "District": district,
            "Village": village,
            "PIN_Code": pincode,
            "Survey_Number": survey_number,
            "Land_Area": land_area,
            "Land_Type": land_type,
            "Guidance_Value_Per_Sqft": guidance_per_sqft,
            "Total_Guidance_Value": total_guidance_value,
            "Market_Value_Per_Sqft": market_per_sqft,
            "Total_Market_Value": total_market_value,
            "Nearby_Avg_Value_Per_Sqft": avg_nearby_price_per_sqft,
            "Total_Nearby_Avg_Value": total_nearby_avg_value,
            "Gender": gender,
            "Married": married,
            "Dependents": dependents,
            "Education": education,
            "Self_Employed": self_employed,
            "Applicant_Income": app_income,
            "Coapplicant_Income": co_income,
            "Total_Income": total_income,
            "Credit_History": credit_history,
            "Property_Area": property_area,
            "Loan_Amount": loan_amount,
            "Loan_Amount_Term": loan_term,
            "LTV_Ratio": actual_ltv,
            "DTI_Ratio": dti,
            "Risk_Score": risk_score,
            "Loan_Approved": loan_approved
        })
        
    df = pd.DataFrame(records)
    df.to_csv("property_loan_data.csv", index=False)
    print("Successfully generated property_loan_data.csv with", num_records, "records.")

if __name__ == "__main__":
    generate_records()
