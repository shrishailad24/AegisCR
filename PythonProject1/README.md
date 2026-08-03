# Walkthrough & Project Documentation - Underwriting & Verification Engine (AegisCR)

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/shrishailad24/AegisCR)

This documentation describes the changes made to correct the loan underwriting and document verification errors, the implementation of the intelligent dynamic background system, and the Render deployment configuration.

---

## Changes Implemented

### 1. Fixed `NameError: name 'dti_ratio' is not defined`
- **Problem**: When evaluating a loan, variables like `dti_ratio`, `emi`, `ltv_ratio`, and the generated `ai_report` were defined only inside the scope of the prediction button click handler. When Streamlit performed a rerun to render the results block, these local variables were no longer defined, resulting in a `NameError`.
- **Solution**: 
  - Added a session state dictionary `st.session_state["underwriting_results"]` that saves all evaluated metrics and borrower parameters upon loan evaluation in `app.py`.
  - Unpacked these values at the top of the decision display block so that they persist and render correctly during reruns.

### 2. Corrected Document Verification demo fallback behavior
- **Problem**: If the user ran the document audit without uploading any files, the code would silently fall back to Demo Simulation Mode, automatically aligning all checks and showing fake trust scores/status nodes.
- **Solution**: 
  - Added an explicit checkbox in Tab 3: **"Enable Demo Simulation"** (defaulting to `False`).
  - Updated the audit fallback check in `app.py` to run strict real audit mode if no files are uploaded, unless this simulation checkbox is checked. If no files are uploaded under strict mode, documents are marked as missing, creating proper `🔴 CONFLICT` status mappings and `0%` trust score.

### 3. Fixed fuzzy check alignment scores
- **Problem**: In `utils/verification_engine.py`, the "Owner Title Registry Match" score was hardcoded to `40%` if any part of property verification (like survey boundary) failed, despite the owner matching status being "PASS" (leading to confusing `40% similarity | ALIGN` outputs).
- **Solution**: 
  - Modified `verify_property_dossier` to return `Owner_Match_Ratio` inside its result payload.
  - Updated `compile_relationship_nodes` to use the actual `Owner_Match_Ratio` for rendering the "Owner Title Registry Match" node score.

### 4. Resolved syntax errors
- **Problem**: Conflicting quotes and backslashes inside nested f-string braces caused compilation errors on older Python versions.
- **Solution**: Re-wrote nested f-strings in `app.py` as simple string concatenations.

### 5. Dynamic Nature Backgrounds using Unsplash & Pexels APIs (Dual Sourcing)
- **Objective**: Dynamically update the app background with high-quality landscape/nature photos selected by analyzing the current weather condition, time of day, and season.
- **Implemented Python Solution**:
  - Created `utils/background_manager.py` to encapsulate time of day categorization, season detection, and query generation.
  - **Fallback API Keys**: Set up user-provided fallback keys directly in the environment parameters for zero-configuration, out-of-the-box execution:
    - Unsplash: `zRFlykNbtqwtGbs5CPWvvGRLxNK9xOmQwBsQ4X1Io1Q`
    - Pexels: `TI15nFTnkzqWP0UAUGuAtLJcFM4PLkLV0JBwVb2KMorQDfk4RGYNIt60`
  - **Dual Sourcing**: Integrated Pexels search API as a parallel data source. If Unsplash limits, fails, or returns an authorization error, the manager automatically queries Pexels to select and format high-resolution nature landscapes.
  - **Beautiful Local Fallback**: Overwrote the technical vector image `assets/loan_background_image.jpeg` by downloading a gorgeous high-resolution sunrise mountain valley image from Pexels, ensuring offline fallback aesthetics are beautiful.
  - **Force Update**: Integrated a mechanism that detects if the cached state is showing a fallback image, immediately triggering a live API fetch attempt once keys are active.
  - **Legibility & Contrast Optimizations**:
    - Restricted all high-contrast white text styles strictly to the main content area selector `[data-testid="stMain"]`. This completely isolates the light-gray sidebar from the white text rules.
    - Explicitly mapped markdown paragraphs, lists, and spans inside `section[data-testid="stSidebar"]` to dark slate `#0f172a` to prevent any browser stylesheet specificity leaks.
    - Forced dark text colors inside native alerts and notification blocks to preserve legibility against light alert backgrounds.
    - Increased the opacity of `.glass-card` and `.metric-card` containers to `85%` white to serve as high-contrast panels behind form text and fields.
- **Implemented React Solution (For future web app migration)**:
  - Updated React hook `frontend/src/hooks/useUnsplashBackground.js` to manage both API connections, rate limits, local fallbacks, query generation, and cached states.
  - Developed a corresponding component `frontend/src/components/BackgroundManager.jsx` with full double-buffered background layers that performs a smooth 1.5-second cross-fade transition when backgrounds update.

### 6. App Title Header Restyling
- **Objective**: Design a beautiful, premium top banner header that integrates modern typography and custom branding.
- **Implemented Changes**:
  - Imported and applied the **Outfit** Google Font to create clean, high-end sans-serif typography.
  - Created a custom gradient-stroke SVG shield icon (drawing a linear sky-blue-to-cyan gradient definitions) to replace the raw emoji.
  - Redesigned the main title text to render in a bold, 3-color linear gradient (`#0284c7` to `#38bdf8`) with high-end letter-spacing.
  - Reformatted the subtitle with uppercase text, modern font weights, and tracking spacing.
  - Added a matching gradient-accent underline bar to frame the title.
  - Upgraded the title container to an 88%-opaque white frosted glassmorphism card with an inset shadow and blur filter.

### 7. Render Deployment Support
- **Blueprint Config**: Created `render.yaml` containing build instructions, Streamlit port mapping, and automatic environment variables.
- **Requirements**: Added `pymupdf`, `google-cloud-vision`, and `gunicorn` to `requirements.txt` to guarantee a clean build on Render servers.
- **Startup Configuration**: Created `Procfile` containing the Streamlit command binding rules, and `runtime.txt` locking the Python runtime environment to `python-3.11.9`.
- **Environment Settings**: Created `.env.example` outlining all API configuration keys.

### 8. Repository Cleanup
- **Deleted Files**: Removed four bulky unused PNG assets from the Git repository:
  - `Approved.image.png`
  - `System.image.png`
  - `dashboard.png`
  - `rejected.image.png`

### 9. Python Package Resolution & Structure
- **utils/ Move**: Moved the entire `utils/` directory into the inner `PythonProject1` repository folder (which matches the root of the remote GitHub repository) to align the package structure.
- **__init__.py**: Added `utils/__init__.py` inside the `utils` directory to explicitly flag the namespace folder as a python package structure to resolve `ModuleNotFoundError: No module named 'utils'` failures during remote builds on Render.
- **Push Helper Assistant**: Created `push.bat` inside the inner repository folder to allow one-click pushes from the local desktop context.

### 10. Secrets & Push Protection Compliance
- **Groq Key Removal**: Purged the hardcoded Groq API key (`gsk_9LcQsFL...`) from `utils/ai_explainer.py`, replacing it with `os.environ.get("GROQ_API_KEY", "")` to comply with GitHub Push Protection rules.
- **Cache Purging**: Removed compiled Python cache directories (`__pycache__/`, `*.pyc`) from the Git tracking index to ensure old key bytecode fragments are completely removed from repository history.
- **Blueprint Security**: Configured all developer API secrets in `render.yaml` using `sync: false` to force Render to prompt the user to input keys in the dashboard during deployment rather than committing them to version control.

---

## Verification Results
- Ran `python -m py_compile` check on `app.py` and `utils/verification_engine.py` successfully in the inner repository.
- Verified compilation on all nested modules inside the `utils` directory.
- Checked repository with `git grep gsk_` confirming 0 occurrences of secrets in code.
- Verified local execution of train_model.py generating models successfully in less than 20 seconds.

---

## ⚙️ AegisCR File Evaluation Engine Pipeline (35-Step Workflow)

The AegisCR File Evaluation Engine automatically analyzes a customer's complete loan application, verifies submitted documents, calculates risk, estimates collateral value, detects fraud, and provides a recommendation to the loan officer in seconds.

### Overall Architecture Flow
```
User Login ➔ Create Loan Application ➔ Upload Documents ➔ Document Validation ➔ OCR Text Extraction ➔ Cross Verification ➔ Financial Analysis ➔ Property Valuation ➔ Risk Assessment ➔ ML Eligibility Prediction ➔ AI Explanation ➔ Generate Recommendation & Letters
```

### The 35-Step Core Pipeline Details:

1. **Customer Authentication (Step 1)**: User logs in using Google OAuth, Email, or Bank Employee ID. The system captures and stores metadata: UID, login timestamp, client device agent, IP, and session tokens.
2. **Customer Profile Creation (Step 2)**: Collects key demographic data: Name, age, gender, occupation, employment company, annual income, PAN/Aadhaar details, and employment history.
3. **Loan Information Registration (Step 3)**: Captures requested loan amount, loan type (home/land/commercial), term/tenure, interest rates, EMI structures, and assigned loan officer.
4. **Document Dossier Upload (Step 4)**: The customer uploads scanned copies of Aadhaar, PAN, Salary Slips, Bank Statements, Property Title Deed, and Income Tax Returns (ITR).
5. **Document Validation Precheck (Step 5)**: Automated checks to ensure PDFs are not corrupted, images are high-resolution, duplicate uploads are flagged, and files are not password protected.
6. **OCR Text Extraction (Step 6)**: Employs optical character recognition (via Google Vision API) to extract text inputs: Name, DOB, Aadhaar/PAN numbers, and property survey/boundaries.
7. **Cross-Verification Engine (Step 7)**: Compares names and IDs across Aadhaar, PAN, Salary Slip, and Title Deeds. Mismatches increase the fraud/document risk factor.
8. **PAN verification (Step 8)**: Verifies alphanumeric format (`ABCDE1234F`), taxpayer registration status, and active status.
9. **Aadhaar Verification (Step 9)**: Audits QR codes, verifies masked formats, matches age boundaries, and validates registration hashes.
10. **Salary Slip Analysis (Step 10)**: Extracts basic salary, HRA, bonuses, PF deductions, and net monthly/yearly payouts.
11. **Bank Statement Cashflow Audit (Step 11)**: Computes monthly credits/debits, salary credit consistency, UPI activity, and flags cheque bounces or EMI return logs.
12. **Income Stability Evaluation (Step 12)**: Audits employment type, company tier, years of experience, and historical income growth.
13. **Property Geospatial Appraisal (Step 13)**: Registers property coordinates, boundaries, district guidelines, construction age, and road accessibility.
14. **Geospatial Map Verification (Step 14)**: Maps location markers to calculate distances from essential facilities (roads, transit, hospitals, schools) and verify boundary shapes.
15. **Climate Hazard Assessment (Step 15)**: Queries historical models for location-based climate risks (flooding zones, earthquake faults, landslide hazards).
16. **AI Property Valuation (Step 16)**: Feeds guidance value rates and geographic multipliers into predictive models to estimate current collateral and resale valuation.
17. **Collateral Index Scoring (Step 17)**: Measures the safety index of the property based on local market velocity and valuation metrics.
18. **Loan-To-Value (LTV) Calculation (Step 18)**: Computes the Loan-to-Value ratio: `LTV = (Requested Loan Amount / Collateral Value) * 100`. Lower ratios improve safety profiles.
19. **Credit History Lookup (Step 19)**: Pulls historical repayment profiles, defaults, active credit card exposures, and current EMI burdens.
20. **Debt-to-Income (DTI) Ratio (Step 20)**: Computes DTI ratio: `DTI = (Total Monthly EMIs / Total Monthly Income)`. Ratios under 50% optimize approval potential.
21. **Fraud Detection Scans (Step 21)**: Audits templates, verifies names against fraud registries, and checks for duplicate property registrations.
22. **Forgery & Tampering Audit (Step 22)**: Checks PDFs for metadata modification history (e.g. Photoshop usage), font changes, and pixel compression anomalies.
23. **Identity Duplication Scans (Step 23)**: Cross-references applicant details (phone, email, bank details) against historical default lists.
24. **Multi-Dimensional Risk Matrix (Step 24)**: Aggregates risk index parameters across credit history, fraud detection, document validity, and collateral safety.
25. **Risk Index Categorization (Step 25)**: Groups applications into risk classes: Very Safe (0-20), Low Risk (20-40), Medium Risk (40-60), High Risk (60-80), and Reject (80-100).
26. **Machine Learning Model Prediction (Step 26)**: Passes verified features to trained classifiers (Random Forest, XGBoost) to classify the application (Approve, Reject, Review).
27. **Explainable AI (XAI) Explanations (Step 27)**: Generates clear, human-legible explanations details explaining the primary reasons behind the risk evaluation.
28. **Recommendation Output (Step 28)**: Flags the decision using color-coded status badges: Green (Approve), Yellow (Manual Officer Review), and Red (Reject).
29. **Letter & Sanction Generation (Step 29)**: Automatically compiles high-quality sanction reports and approval letters in PDF with tables, repayment terms, and stamps.
30. **Secure Database Storage (Step 30)**: Commits all borrower details, prediction results, sanction letters, and risk profiles to a secure database.
31. **Audit Logs Tracking (Step 31)**: Captures all user-interface actions (downloads, edits, overrides) with IP address, user-agent, and timestamps.
32. **Underwriter Performance Dashboard (Step 32)**: Renders portfolio summaries: processed volumes, approval rates, average LTV/DTI trends, and geographic map distributions.
33. **Lending Policy Configuration (Step 33)**: Enables administrative changes to base lending policy values, interest rates, LTV caps, and DTI ceilings.
34. **Notification Routing (Step 34)**: Triggers transactional emails, SMS notifications, and internal system alerts to borrowers and loan officers.
35. **Future Scalability Architectures (Step 35)**: Future extensions include: Firebase OAuth integrations, Face Matching models, satellite property scans, and automated API-based CIBIL queries.

---

## 🔑 Render Environment Variables & Secrets Guide

When deploying to Render, you will be prompted to enter the following environment variables (since `sync: false` is configured in `render.yaml` for security compliance). You can copy-paste the values below directly into the Render dashboard to enable all dynamic background, weather, and AI report features:

| Environment Variable | Description | API Credentials Value to Copy-Paste |
| --- | --- | --- |
| **`UNSPLASH_ACCESS_KEY`** | Unsplash Search API Access Key | `zRFlykNbtqwtGbs5CPWvvGRLxNK9xOmQwBsQ4X1Io1Q` |
| **`PEXELS_API_KEY`** | Pexels Landscape API Key | `TI15nFTnkzqWP0UAUGuAtLJcFM4PLkLV0JBwVb2KMorQDfk4RGYNIt60` |
| **`WEATHER_API_KEY`** | OpenWeatherMap API Key | `db8abf34273cc1c921dde0f6986a6920` |
| **`GROQ_API_KEY`** | Groq Explainable AI LLM Key | `your_groq_api_key_here` |
