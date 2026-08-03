# AegisCR Production Bug Tracker

This document tracks system exceptions, regression errors, and logical bugs identified and resolved during development.

---

| Bug ID | Component | Description / Error Message | Status | Resolution Detail |
| :--- | :--- | :--- | :--- | :--- |
| **BUG-001** | Valuation / ML | `FileNotFoundError: [Errno 2] No such file or directory: 'valuation_model.pkl'` on Render. | **FIXED** | Modified the build command in `render.yaml` to trigger `python train_model.py` dynamically during the build pipeline instead of committing binaries to Git. |
| **BUG-002** | Security / Git | `Groq API Key exposed` push protection block. | **FIXED** | Removed hardcoded credential keys from `ai_explainer.py` and replaced them with `os.getenv("GROQ_API_KEY")`. Purged pycache. |
| **BUG-003** | Compliance / OCR | Trust Score displays `99.4%` even when no document uploads are present (mock defaults bypass). | **FIXED** | Enforced strict file upload requirements checking for Aadhaar, PAN, and slips in Tab 3. Added `"checked": True` session state hooks. |
| **BUG-004** | Underwriting UI | `NameError: name 'dti_ratio' is not defined` during Streamlit page refresh/rerun. | **FIXED** | Created an `underwriting_results` session state dictionary to persist all calculated results across Streamlit rerun cycles. |
| **BUG-005** | Compiler / core | `SyntaxError` on older Python versions due to nested quotes in f-strings. | **FIXED** | Refactored complex nested f-strings into standard string additions. |
| **BUG-006** | Valuation / UI | Model prediction crashes on empty/zero area inputs. | **FIXED** | Added UI-level empty parameter validation pre-checks in Tab 2 to prevent calculation calls if inputs are missing or non-positive. |
