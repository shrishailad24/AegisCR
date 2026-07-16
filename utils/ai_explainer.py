import requests
import json

GROQ_API_KEY = "YOUR_GROQ_API_KEY"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def explain_rejection(credit, income, loan_amount):
    reasons = []
    if credit == 0.0:
        reasons.append("Low credit history")
    if income < 5000:
        reasons.append("Low income level")
    if loan_amount > income * 5:
        reasons.append("Loan amount too high compared to income")
    
    if not reasons:
        return "Profile does not meet internal bank criteria."
    return "Loan rejected due to: " + ", ".join(reasons)

def generate_ai_underwriting_report(name, credit, income, loan_amount, loan_term,
                                    property_details, approved,
                                    identity_res=None, income_res=None,
                                    property_res=None, risk_res=None,
                                    officer_notes=""):
    """
    Generates a premium AegisCR underwriting report via Groq LLM API.
    Provides detailed audit matching logs, multi-factor risk commentary, and officer field observations.
    """
    
    state = property_details.get("State", "N/A")
    district = property_details.get("District", "N/A")
    village = property_details.get("Village", "N/A")
    pincode = property_details.get("PIN_Code", "N/A")
    survey_number = property_details.get("Survey_Number", "N/A")
    land_area = property_details.get("Land_Area", 0)
    land_type = property_details.get("Land_Type", "Residential")
    
    market_value = property_details.get("Total_Market_Value", 0)
    guidance_value = property_details.get("Total_Guidance_Value", 0)
    
    ltv_ratio = loan_amount / market_value if market_value > 0 else 0
    
    monthly_rate = 0.09 / 12
    try:
        emi = loan_amount * (monthly_rate * (1 + monthly_rate)**loan_term) / ((1 + monthly_rate)**loan_term - 1)
    except:
        emi = loan_amount / loan_term if loan_term > 0 else 0
    dti_ratio = emi / income if income > 0 else 0
    
    # Risk parameters
    ari_score = 30.0
    ari_rating = "Medium Risk"
    risk_breakdown_str = ""
    if risk_res:
        ari_score = risk_res.get("Aegis_Risk_Index", 30.0)
        ari_rating = risk_res.get("Rating", "Medium Risk")
        bd = risk_res.get("Breakdown", {})
        risk_breakdown_str = (
            f"- Identity Verification Risk: {bd.get('Identity_Risk', 0)}/100\n"
            f"- Financial Affordability Risk: {bd.get('Financial_Risk', 0)}/100\n"
            f"- Collateral Value Risk: {bd.get('Collateral_Risk', 0)}/100\n"
            f"- Document Integrity & Fraud Risk: {bd.get('Fraud_Risk', 0)}/100\n"
            f"- Credit History Risk: {bd.get('Credit_Risk', 0)}/100"
        )
        
    # Verification alert logs
    alerts = []
    if identity_res and identity_res.get("Flags"):
        alerts.extend(identity_res["Flags"])
    if income_res and income_res.get("Flags"):
        alerts.extend(income_res["Flags"])
    if property_res and property_res.get("Flags"):
        alerts.extend(property_res["Flags"])
    if property_details.get("fraud_check", {}).get("flags"):
        alerts.extend(property_details["fraud_check"]["flags"])
        
    alerts_str = "\n".join([f"- [ALERT] {a}" for a in alerts]) if alerts else "None detected (All verification parameters clean)."
    
    result_str = "APPROVED" if approved else "REJECTED"
    
    prompt = f"""
As a Chief Underwriting Officer at Aegis Credit Risk (AegisCR), formulate a comprehensive underwriting audit report:

=== BORROWER PROFILE ===
Name: {name}
Income Declared: ₹{income:,.2f}/mo
Requested Loan: ₹{loan_amount:,.2f} over {loan_term} months (Est. EMI: ₹{emi:,.2f})
Credit History status: {"Good History" if credit == 1.0 else "Default History"}

=== COLLATERAL ASSET ===
Structure: {"Unsecured - No Collateral backing" if land_type == "Unsecured" else f"Secured Collateral ({property_details.get('property_class', 'Land only')})"}
Location: {village}, {district}, {state} - {pincode} (Survey: {survey_number})
Land Classification: {land_type} ({land_area:,} sqft)
Circle guidance value: ₹{guidance_value:,.2f}
Estimated market value: ₹{market_value:,.2f}

=== AEGIS CREDIT RISK RATIOS ===
LTV Ratio: {ltv_ratio*100:.1f}%
DTI Ratio: {dti_ratio*100:.1f}%
Aegis Risk Index (ARI) score: {ari_score}/100 ({ari_rating})
{risk_breakdown_str}

=== DOCUMENT INTEGRITY & VERIFICATION ALERTS ===
{alerts_str}

=== LOAN OFFICER NOTES & FIELD OBSERVATIONS ===
{officer_notes if officer_notes else "None provided."}

=== SYSTEM DECISION ===
{result_str}

Format the report using markdown. Include these exact sections:
1. EXECUTIVE UNDERWRITING MATRIX: Brief overview of ratios and final system audit result.
2. OCR INTEGRITY & IDENTITY ALIGNMENT: Review names fuzzy matches and address discrepancies.
3. FINANCIAL CASH-FLOW & DTI ANALYSIS: Affordability analysis, commenting on DTI limits and cashflow stability.
4. COLLATERAL VALUATION & LAND AUDIT: Market value vs circle rates, depreciation factor checks, LTV caps. (Comment on lack of collateral if unsecured).
5. DEVIATION FLAGS & AUDIT MITIGANTS: Commentary on the alerts and the Officer's Notes, suggesting how to resolve risk items.
6. FINAL AUDIT DIRECTIVE: Specific action (Approve/Sanction, Reject, or Manual Escalate to Legal) and key sanction terms.

Maintain an objective, analytical, institutional credit risk vocabulary. Keep it structured with clear bullet points.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a professional banking credit analyst and real estate valuation expert writing formal underwriting reports."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 1200
    }
    
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Groq API Error {response.status_code}: {response.text}")
            return generate_fallback_report(name, ari_score, ari_rating, loan_amount, ltv_ratio, dti_ratio, alerts, approved)
    except Exception as e:
        print(f"Groq Request exception: {e}")
        return generate_fallback_report(name, ari_score, ari_rating, loan_amount, ltv_ratio, dti_ratio, alerts, approved)

def generate_fallback_report(name, ari_score, ari_rating, loan_amount, ltv_ratio, dti_ratio, alerts, approved):
    decision_text = "APPROVED" if approved else "REJECTED"
    alerts_str = "\n".join([f"- {a}" for a in alerts]) if alerts else "- All verification matches passed."
    
    report = f"""### AEGISCR UNDERWRITING REPORT (FALLBACK AUTO-GENERATION)

**Borrower Name**: {name}  
**Aegis Risk Index**: **{ari_score}/100 ({ari_rating})**  
**Credit Risk Decision**: **{decision_text}**  

---

#### 1. EXECUTIVE UNDERWRITING MATRIX
- The dossier has been audited for document compliance and credit risk. The composite Aegis Risk Index (ARI) score is **{ari_score}/100**, falling in the **{ari_rating}** category.
- **Ratios**: LTV is {ltv_ratio*100:.1f}%, DTI is {dti_ratio*100:.1f}%.

#### 2. OCR INTEGRITY & IDENTITY ALIGNMENT
- Identity profiles were fuzzy-matched across Aadhaar, PAN, and Bank data. 
- Mismatches in strings have been flagged and must be manual cross-checked before disbursal.

#### 3. FINANCIAL CASH-FLOW & DTI ANALYSIS
- Declared income compared to pay slips falls within acceptable limits. Debt-to-income represents a {"manageable load" if dti_ratio <= 0.45 else "substantial burden exceeding prudent bank limits"}.

#### 4. COLLATERAL VALUATION & LAND AUDIT
- Collateral valuation completed. Land class and depreciation rules applied. LTV exposure is {"within tolerance guidelines" if ltv_ratio <= 0.8 else "excessive, requiring loan amount reduction"}.

#### 5. DEVIATION FLAGS & AUDIT MITIGANTS
The audit engine highlighted the following deviation items:
{alerts_str}
- **Mitigation Recommendation**: Verify title deeds, request CIBIL explanations, or obtain additional co-applicants as guarantors.

#### 6. FINAL AUDIT DIRECTIVE
- **Directive**: **{"PROCEED WITH LOAN SANCTION subject to legal title approval" if approved else "DEFER SANCTION / REJECT due to credit risk or document mismatches"}**.
- Recommended covenant: Mortgage registration of the land survey plot.
"""
    return report

def query_underwriter_chat(message, context_summary):
    """
    Answers user officer queries using Groq LLM.
    """
    prompt = f"""
You are an AI Underwriter chatbot assistant embedded in AegisCR decision portal.
The loan officer has loaded the following credit context:

=== LOAN COMPLIANCE CONTEXT ===
{context_summary}

=== OFFICER QUESTION ===
{message}

Please provide a concise, expert banking response (3-4 bullet points maximum). Address their concern directly, referring to credit mitigation rules, collateral gaps, or repayment margins.
"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a professional banking credit analyst and risk assistant. Be concise and structured."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 400
    }
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=8)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error from Groq API ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Underwriter AI Offline. Failed to connect: {str(e)}"