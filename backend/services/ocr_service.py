def audit_uploaded_documents(aadhaar_name, pan_name, sale_deed_name, rtc_owner_name, has_aadhaar, has_pan, has_income, has_deed, has_rtc):
    names = [aadhaar_name.strip(), pan_name.strip(), sale_deed_name.strip(), rtc_owner_name.strip()]
    names = [n for n in names if n]
    
    mismatch = False
    if len(names) > 1:
        first = names[0].lower().replace(" ", "")
        for n in names[1:]:
            curr = n.lower().replace(" ", "")
            if curr != first:
                mismatch = True
                break
                
    trust_score = 98
    if mismatch:
        trust_score = 62
    if not (has_aadhaar and has_pan and has_deed):
        trust_score -= 20
    trust_score = max(30, trust_score)
    
    fraud_score = 12
    reasons = []
    if mismatch:
        fraud_score += 35
        reasons.append("Credential Identity Mismatch flag triggered")
    if not has_rtc:
        fraud_score += 15
        reasons.append("Missing government record RTC/Pahani copy")
        
    return {
        "mismatch": mismatch,
        "trust_score": trust_score,
        "fraud_score": fraud_score,
        "fraud_level": "Low" if fraud_score < 25 else "Medium" if fraud_score < 50 else "High",
        "fraud_reasons": reasons
    }
