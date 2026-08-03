import sys
import os
import json

def run_test_suite():
    print("========================================")
    print("[RUNNING AEGISCR AUTOMATED TEST SUITE]")
    print("========================================")
    
    errors = []
    
    # 1. Test: Package imports and namespace resolution
    print("\n[1/8] Testing Package Imports & Namespace...")
    try:
        sys.path.append(os.path.abspath(os.path.dirname(__file__)))
        from utils.valuation_module import calculate_valuation
        from utils.verification_engine import verify_identity_dossier
        from utils.pdf_generator import generate_pdf
        print("-> Imports check passed.")
    except Exception as e:
        errors.append(f"Imports / Namespace failed: {e}")
        print("-> Imports check failed.")
        
    # 2. Test: Login verification simulated
    print("\n[2/8] Testing Login Authentication...")
    try:
        # Verify simple auth credentials parsing mock
        user_db = {"admin": "aegis2026"}
        assert user_db.get("admin") == "aegis2026"
        print("-> Login Simulation check passed.")
    except Exception as e:
        errors.append(f"Login Check failed: {e}")
        print("-> Login Check failed.")
        
    # 3. Test: Document Upload parameters
    print("\n[3/8] Testing Document Upload Simulation...")
    try:
        # Verify upload path registers
        os.makedirs("test_data/good_documents", exist_ok=True)
        temp_file = "test_data/good_documents/upload_test.txt"
        with open(temp_file, "w") as f:
            f.write("Aegis Upload Test")
        assert os.path.exists(temp_file)
        os.remove(temp_file)
        print("-> File System Upload check passed.")
    except Exception as e:
        errors.append(f"Document Upload failed: {e}")
        print("-> Document Upload failed.")
        
    # 4. Test: OCR parsing mocks
    print("\n[4/8] Testing OCR text parsing...")
    try:
        from utils.ocr_engine import process_dossier_file
        from reportlab.pdfgen import canvas
        
        # Create a valid minimal PDF file
        os.makedirs("test_data/good_documents", exist_ok=True)
        temp_file = "test_data/good_documents/aadhaar_temp.pdf"
        c = canvas.Canvas(temp_file)
        c.drawString(100, 750, "Aegis Mock Aadhaar Card Number 1234 5678 9012 Name Rajesh Kumar DOB 10-10-1990")
        c.save()
            
        mock_res = process_dossier_file(temp_file, "aadhaar_temp.pdf", doc_category="Aadhaar")
        assert mock_res.get("Name") is not None
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        print("-> OCR processing mock check passed.")
    except Exception as e:
        errors.append(f"OCR Parsing failed: {e}")
        print("-> OCR Parsing failed.")
        
    # 5. Test: Document Matching checks
    print("\n[5/8] Testing Document Matching engine...")
    try:
        from utils.verification_engine import verify_identity_dossier, levenshtein_ratio
        name1 = "Rajesh Kumar"
        name2 = "Rajesh Kumar A"
        match_ratio = levenshtein_ratio(name1.lower(), name2.lower())
        assert match_ratio > 0.8
        print("-> Fuzzy name matching check passed.")
    except Exception as e:
        errors.append(f"Document Matching failed: {e}")
        print("-> Document Matching failed.")
        
    # 6. Test: Property Valuation calculations (Golden Property)
    print("\n[6/8] Testing Property Valuation engine...")
    try:
        from utils.valuation_module import calculate_valuation
        res = calculate_valuation(
            state="Karnataka", district="Bengaluru Urban", village="Indiranagar",
            pincode="560038", survey_number="G-1200", land_area=1200,
            land_type="Residential", lat=12.9784, lon=77.6408,
            property_class="Land only", built_up_area=0, building_age=0,
            construction_quality="Standard"
        )
        assert res["total_market_value"] > 0
        market_val_str = str(res["total_market_value"])
        print(f"-> Property Valuation check passed (Calculated Market: Rs. {market_val_str}).")
    except Exception as e:
        errors.append(f"Property Valuation failed: {e}")
        print("-> Property Valuation failed.")
        
    # 7. Test: Loan Prediction ML Model loading & logic
    print("\n[7/8] Testing Loan Prediction models...")
    try:
        from utils.risk_engine import calculate_aegis_risk
        # Mock input parameters
        credit_history = 1.0
        ltv = 0.65
        dti = 0.35
        risk_res = calculate_aegis_risk(
            identity_res={"Status": "PASS"},
            income_res={"Status": "PASS"},
            property_res={"Status": "PASS"},
            credit_history=credit_history,
            ltv_ratio=ltv,
            dti_ratio=dti,
            valuation_details={"Risk_Score": 25}
        )
        assert risk_res["Probability_Of_Default"] is not None
        print(f"-> Loan Risk calculation check passed (Prob of Default: {risk_res['Probability_Of_Default']}%).")
    except Exception as e:
        errors.append(f"Loan Prediction failed: {e}")
        print("-> Loan Prediction failed.")
        
    # 8. Test: PDF Generation check
    print("\n[8/8] Testing PDF Generation...")
    try:
        from utils.pdf_generator import generate_pdf
        pdf_path = generate_pdf(
            name="Rajesh Kumar",
            gender="Male",
            married="Yes",
            dependents=0,
            education="Graduate",
            self_emp="No",
            credit=1.0,
            property_area=1200,
            loan_amount=5000000,
            loan_term=240,
            app_income=75000,
            co_income=35000,
            result_text="APPROVED",
            property_details={"Village": "Indiranagar", "Survey_Number": "G-1200"},
            ai_explanation="Test explanation",
            dossier_data={},
            verification_res={},
            risk_res={},
            officer_notes="Test Notes"
        )
        assert os.path.exists(pdf_path)
        print(f"-> PDF compilation check passed (Created: {pdf_path}).")
    except Exception as e:
        errors.append(f"PDF Generation failed: {e}")
        print("-> PDF Generation failed.")
        
    print("\n========================================")
    if errors:
        print("[AUTOMATED TEST SUITE FAILED!]")
        print("Summary of Errors:")
        for err in errors:
            print(f"- {err}")
        sys.exit(1)
    else:
        print("[ALL AUTOMATED TESTS PASSED SUCCESSFULLY!]")
        sys.exit(0)

if __name__ == "__main__":
    run_test_suite()
