# AegisCR Development Blueprint & Architecture Roadmap

This guide documents the software engineering design patterns, validation pipelines, and release roadmaps for the AegisCR Underwriting Portal.

---

## ⚙️ Modular Underwriting Pipeline Architecture

To maintain high reliability, AegisCR follows a sequential pipeline design where each component runs independently and validates its inputs before passing state to the next stage.

```
  [User Login] (Gmail / Firebase Auth)
        │
        ▼
  [Application Registration] (Unique ID e.g., LN202600001)
        │
        ▼
  [Upload Dossier Validation] (Required vs. Optional check)
        │
        ▼
  [OCR Extraction] (Google Vision / EasyOCR text parsing)
        │
        ▼
  [Data Sanitization] (Regex matching and parsing clean strings)
        │
        ▼
  [Cross-Document Field Matching] (Fuzzy Name, DOB, Address, PAN checks)
        │
        ▼
  [Forensic Brain & Fraud Auditing] (Duplicate scans, metadata tampering checks)
        │
        ▼
  [Property Valuation Engine] (Guidance values, location multipliers)
        │
        ▼
  [Credit History & Repayment Audit] (CIBIL repayment checks)
        │
        ▼
  [ML Underwriting Decision Model] (Random Forest Classification & XAI Explanation)
        │
        ▼
  [Report compiler] (Transactional database sync & Sanction PDF generation)
```

---

## 📂 Document Lifecycle & Verification States

Each uploaded document must transition through a linear lifecycle state. This allows clear progress tracking and easier debugging compared to a single aggregated score.

### Verification States:
1. **⬜ Not Uploaded**: File has not been supplied yet.
2. **📤 Uploaded**: File received successfully and stored in memory.
3. **🔍 OCR Running**: Document processing is in progress.
4. **📄 OCR Complete**: Text annotations extracted successfully.
5. **🔄 Cross Matching**: Fuzzy-matching fields against other verified documents.
6. **🛡️ Fraud Check**: Auditing metadata and file integrity.
7. **✅ Verified**: Document passed all required thresholds.
8. **❌ Failed**: Discrepancies found (e.g., critical mismatch).

### Mandatory vs. Optional Documents
* **Required Documents (Must Upload to evaluate)**:
  * Aadhaar Card
  * PAN Card
  * Salary Slip (or Income Proof)
  * Property Title Deed (Sale Deed)
* **Optional Documents (Can skip - improves confidence scoring)**:
  * Bank Statements
  * Utility Bills
  * Encumbrance Certificates (EC)
  * ITR Forms

---

## 📊 Evaluation & AI Decision Rules

When evaluating similarity scores across documents (e.g. name similarity across Aadhaar, PAN, and Sale Deed):

* **Score > 95%**: Auto-Verified (Safe).
* **Score 80%–95%**: Flagged for **Manual Underwriter Review**.
* **Score < 80%**: Auto-Rejected.

---

## 🛠️ Developer Best Practices & Testing Checklist

To maintain clean code and catch errors early:

### 1. Never Develop Directly on `main`
Always develop features in isolated topic branches:
`git checkout -b feature/firebase-login`

### 2. Isolate Module Testing
Test each component in isolation (e.g., OCR text cleaning, Guidance value lookup) before merging it into the application logic flow.

### 3. Log Every Step
Use detailed step-by-step logs at each critical transition point:
`[INFO] Starting property valuation...`
`[INFO] Loading valuation_model.pkl...`

### 4. Developer Dashboard Checklist
Before deploying, verify that all core service integration nodes are healthy:
- [x] Machine Learning Models Loaded (`valuation_model.pkl`, `loan_model.pkl`)
- [x] OCR System Connection (Google Vision / local EasyOCR fallback)
- [x] Database Connection (PostgreSQL / Firebase)
- [x] External API keys (Unsplash, Pexels, OpenWeatherMap)
