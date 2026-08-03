
 # 🛡️ AegisCR – AI-Powered Credit Risk & Collateral Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

AegisCR is an AI-powered underwriting and collateral appraisal platform designed to help banks, NBFCs, and financial institutions make faster, smarter, and more transparent lending decisions.

The platform combines AI-based credit risk assessment, collateral valuation, geospatial intelligence, OCR-based document verification, explainable AI, and loan analytics into a unified underwriting system.

---

# 🌐 Live Demo

**Application:** https://aegiscr-5.onrender.com

> **Note:** Since the application is hosted on Render's free tier, the first request may take 30–60 seconds while the server wakes up.

---

# ✨ Features

## 🏦 Multi-Loan Underwriting

Supports:

- 🏠 Home Loan
- 🌾 Agriculture Loan
- 🏢 Commercial Property Loan
- 🥇 Gold Loan
- 🚗 Vehicle Loan
- 🚜 Farm Equipment Loan

---

# 🏠 Home Loan Intelligence

### Property Registration

- State
- District
- Taluk
- Village
- Survey Number
- PIN Code

### Geospatial Intelligence

- Interactive Leaflet Map
- Coordinate Capture
- Boundary Mapping
- Guidance Value Lookup
- Market Value Estimation

### Property Details

- Plot Area
- Built-up Area
- Property Type
- Construction Year
- Number of Floors
- Building Condition
- Occupancy Status

### AI Assessment

- Government Guidance Value
- AI Market Valuation
- Loan-to-Value (LTV)
- EMI Estimation
- Risk Analysis
- Explainable AI Recommendation

---

# 🌾 Agriculture Loan Intelligence

### Land Details

- Land Area
- Land Classification
- Crop Type
- Soil Type
- Irrigation Type
- Survey Number

### AI Agriculture Analysis

- Weather Intelligence
- Rainfall Risk
- Drought Risk
- Flood Risk
- Yield Prediction
- Agricultural Risk Score

### AI Recommendation

- Loan Eligibility
- Risk Grade
- Suggested Loan Amount
- Explainable AI Decision

---

# 🏢 Commercial Loan Intelligence

### Commercial Property Analysis

- Plot Area
- Built-up Area
- Commercial Property Type
- Business Category
- Rental Income
- Occupancy Rate
- Road Connectivity
- Market Demand

### Commercial Valuation

- AI Market Value
- Commercial Risk Score
- Rental Yield Analysis
- Investment Score
- LTV Calculation

---

# 🚗 Vehicle Loan

- Vehicle Valuation
- Depreciation Analysis
- Vehicle Age
- Insurance Verification
- RC Verification
- AI Loan Recommendation

---

# 🥇 Gold Loan

- Gold Purity Analysis
- Ornament Weight
- Market Gold Price
- Eligible Loan Amount
- Risk Assessment

---

# 🚜 Farm Equipment Loan

Supports valuation of:

- Tractor
- Harvester
- Rotavator
- Seeder
- Cultivator
- Sprayer
- Irrigation Equipment

Features:

- Equipment Age
- Depreciation
- Condition Assessment
- Market Value
- AI Risk Score

---

# 📍 Property Intelligence

- Property Registration
- Survey Verification
- Latitude & Longitude Capture
- Interactive GIS Mapping
- Property Boundary Identification
- Guidance Value Lookup
- AI Market Valuation
- Fraud Detection Indicators

---

# 📄 OCR & Document Verification

Supports:

- Aadhaar
- PAN
- Salary Slip
- Bank Statement
- Income Certificate
- RTC / Pahani
- Sale Deed
- Property Documents

Features:

- OCR Extraction
- Cross-document Validation
- AI Fraud Detection
- Confidence Score
- Explainable Verification

---

# 🌦 Weather Intelligence

Integrated Weather Analysis:

- Current Weather
- Rainfall
- Temperature
- Flood Risk
- Drought Risk
- Agriculture Suitability

---

# 🤖 Explainable AI

Every prediction includes:

- Confidence Score
- Risk Factors
- Decision Explanation
- Recommendation
- Approval Probability

---

# 📊 Analytics Dashboard

- Portfolio Dashboard
- Loan Distribution
- Approval Statistics
- Risk Categories
- Property Insights
- AI Performance Metrics

---

# 📑 PDF Report Generation

Automatically generates:

- Property Valuation Report
- Loan Assessment Report
- Credit Risk Report
- AI Recommendation Report
- Underwriting Summary

---

# 🛠 Technology Stack

## Frontend

- Streamlit
- HTML
- CSS

## Backend

- Python

## Machine Learning

- Scikit-learn
- Pandas
- NumPy

## Geospatial

- Folium
- Leaflet

## OCR

- Google Vision API

## AI

- Explainable AI
- Credit Risk Prediction
- Property Valuation Models

## Deployment

- Render

---

# 📂 Project Structure

```
AegisCR
│
├── app.py
├── assets/
├── backend/
├── credentials/
├── database/
├── frontend/
├── models/
├── pages/
├── services/
├── test_data/
├── utils/
├── .env.example
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/shrishailad24/AegisCR.git
```

Move into the project

```bash
cd AegisCR
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create an environment file

```bash
cp .env.example .env
```

Add your API keys to `.env`.

Run the application

```bash
streamlit run app.py
```

---

# 🔐 Environment Variables

Example:

```env
OPENAI_API_KEY=
GROQ_API_KEY=
GOOGLE_MAPS_API_KEY=
GOOGLE_VISION_API_KEY=
OPENWEATHER_API_KEY=
MONGODB_URI=
```

Never commit your `.env` file or credentials to GitHub.

---

# 📌 Future Enhancements

- CIBIL Integration
- Aadhaar e-KYC
- PAN Verification
- Drone-based Land Survey
- Satellite Image Analysis
- Blockchain Document Verification
- Digital Signature Support
- Multi-language Support
- Mobile Application
- Banking API Integration

---

# ⚠ Disclaimer

AegisCR is developed for educational, research, and prototype purposes. It should not be used as the sole basis for real-world lending decisions without proper regulatory compliance, institutional validation, and legal approval.

---

# 👨‍💻 Developer

**Shrishail Hebballi**

B.E. Artificial Intelligence & Data Science

BMS College of Engineering, Bengaluru

GitHub: https://github.com/shrishailad24

---

## ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.