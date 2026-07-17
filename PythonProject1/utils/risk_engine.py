def calculate_aegis_risk(identity_res, income_res, property_res, credit_history,
                         ltv_ratio, dti_ratio, valuation_details):
    """
    Computes individual risk profiles, aggregates them into the Aegis Risk Index (ARI),
    and outputs a structured Explainable AI (XAI) waterfall penalty breakup.
    """
    
    # 1. Identity Risk (Weight: 10%)
    id_risk = 0
    id_penalty = 0
    if identity_res:
        name_status = identity_res.get("Name_Status", "PASS")
        dob_status = identity_res.get("DOB_Status", "PASS")
        
        if name_status == "WARNING":
            id_risk += 25
            id_penalty += 8
        elif name_status == "FAIL":
            id_risk += 75
            id_penalty += 20
            
        if dob_status == "FAIL":
            id_risk += 25
            id_penalty += 7
            
        id_risk = min(id_risk, 100)
    else:
        id_risk = 50
        id_penalty = 15
        
    # 2. Financial Affordability Risk (Weight: 25%)
    fin_risk = 0
    dti_penalty = 0
    income_penalty = 0
    
    if dti_ratio <= 0.35:
        fin_risk += int(dti_ratio * 100)
        dti_penalty = int(dti_ratio * 20)
    elif dti_ratio <= 0.50:
        fin_risk += 35 + int((dti_ratio - 0.35) * 200)
        dti_penalty = 12 + int((dti_ratio - 0.35) * 80)
    else:
        fin_risk += 65 + int((dti_ratio - 0.50) * 150)
        dti_penalty = 25 + int((dti_ratio - 0.50) * 60)
        
    if income_res:
        inc_status = income_res.get("Status", "PASS")
        if inc_status == "WARNING":
            fin_risk += 20
            income_penalty += 6
        elif inc_status == "FAIL":
            fin_risk += 45
            income_penalty += 15
            
    fin_risk = min(fin_risk, 100)
    
    # 3. Collateral Risk (Weight: 20%)
    col_risk = 0
    ltv_penalty = 0
    prop_penalty = 0
    is_unsecured = valuation_details.get("Land_Type") == "Unsecured"
    
    if is_unsecured:
        col_risk = 70
        ltv_penalty = 12  # Fixed premium penalty for unsecured exposure
    else:
        if ltv_ratio <= 0.60:
            col_risk += int(ltv_ratio * 50)
            ltv_penalty = int(ltv_ratio * 15)
        elif ltv_ratio <= 0.80:
            col_risk += 30 + int((ltv_ratio - 0.60) * 200)
            ltv_penalty = 10 + int((ltv_ratio - 0.60) * 80)
        else:
            col_risk += 70 + int((ltv_ratio - 0.80) * 150)
            ltv_penalty = 22 + int((ltv_ratio - 0.80) * 70)
            
        land_type = valuation_details.get("Land_Type", "Residential")
        if land_type == "Agricultural":
            col_risk += 15
            prop_penalty += 4
            
        if property_res:
            if not property_res.get("Is_Verified", True):
                col_risk += 35
                prop_penalty += 12
                
    col_risk = min(col_risk, 100)
    
    # 4. Document Fraud Risk (Weight: 10%)
    fraud_risk = 0
    fraud_penalty = 0
    if is_unsecured:
        fraud_risk = 10
    else:
        fraud_check = valuation_details.get("fraud_check", {})
        fraud_status = fraud_check.get("status", "PASS")
        
        if fraud_status == "WARNING":
            fraud_risk += 30
            fraud_penalty += 10
        elif fraud_status == "HIGH RISK" or fraud_status == "FAIL":
            fraud_risk += 80
            fraud_penalty += 25
            
    fraud_risk = min(fraud_risk, 100)
    
    # 5. Credit Bureau Risk (Weight: 35%)
    cred_risk = 10 if credit_history == 1.0 else 85
    cred_penalty = 5 if credit_history == 1.0 else 35
    
    # ================= AGGREGATE RISK (ARI) =================
    ari = (
        0.10 * id_risk + 
        0.25 * fin_risk + 
        0.20 * col_risk + 
        0.10 * fraud_risk + 
        0.35 * cred_risk
    )
    ari = round(ari, 1)
    
    # Add cashflow stability variance adjustments to the final ARI score if calculated
    cashflow_penalty = 0
    if "trust_score" in valuation_details:
        trust_val = valuation_details["trust_score"]
        if trust_val < 90:
            cashflow_penalty += int((90 - trust_val) * 0.5)
            ari = min(98.0, ari + cashflow_penalty)
            
    if ari < 30.0:
        rating = "Low Risk"
        color = "#10b981" # Green
    elif ari < 50.0:
        rating = "Medium Risk"
        color = "#f59e0b" # Amber
    elif ari < 75.0:
        rating = "High Risk"
        color = "#ef4444" # Red
    else:
        rating = "Critical Risk"
        color = "#880e4f"
        
    z = (ari - 65.0) / 10.0
    pd_rate = 1 / (1 + 2.71828**(-z))
    pd_rate = round(pd_rate * 100, 2)
    pd_rate = max(0.5, min(pd_rate, 99.0))
    
    # Formulate XAI list
    xai_waterfall = []
    if cred_penalty > 5:
        xai_waterfall.append({"factor": "Credit Bureau Bureau Defaults", "impact": f"+{cred_penalty}%"})
    if dti_penalty > 10:
        xai_waterfall.append({"factor": "Debt-to-Income (DTI) Burden", "impact": f"+{dti_penalty}%"})
    if ltv_penalty > 10:
        xai_waterfall.append({"factor": "Collateral Loan-to-Value exposure", "impact": f"+{ltv_penalty}%"})
    if id_penalty > 0:
        xai_waterfall.append({"factor": "Identity fuzzy inconsistencies", "impact": f"+{id_penalty}%"})
    if income_penalty > 0:
        xai_waterfall.append({"factor": "Income declared vs slip mismatch", "impact": f"+{income_penalty}%"})
    if prop_penalty > 0:
        xai_waterfall.append({"factor": "Sale Deed Registry conflict", "impact": f"+{prop_penalty}%"})
    if fraud_penalty > 0:
        xai_waterfall.append({"factor": "Fraud Brain metadata anomaly", "impact": f"+{fraud_penalty}%"})
    if cashflow_penalty > 0:
        xai_waterfall.append({"factor": "EMI Bounces / Cash flow leaks", "impact": f"+{cashflow_penalty}%"})
        
    if not xai_waterfall:
        xai_waterfall.append({"factor": "Base Low Risk Profile Guidelines", "impact": "Aligned"})
        
    return {
        "Aegis_Risk_Index": ari,
        "Rating": rating,
        "Color": color,
        "Probability_Of_Default": pd_rate,
        "XAI_Waterfall": xai_waterfall,
        "Breakdown": {
            "Identity_Risk": id_risk,
            "Financial_Risk": fin_risk,
            "Collateral_Risk": col_risk,
            "Fraud_Risk": fraud_risk,
            "Credit_Risk": cred_risk
        }
    }
