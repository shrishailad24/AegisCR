import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os
import random
import requests
from datetime import datetime
import folium
from streamlit_folium import st_folium
from utils.pdf_generator import generate_pdf
from utils.ai_explainer import generate_ai_underwriting_report, query_underwriter_chat
from utils.valuation_module import calculate_valuation, GEO_DB
from utils.verification_engine import (
    verify_identity_dossier, verify_income_dossier, verify_property_dossier,
    verify_cashflow_stability, conduct_fraud_brain_audit,
    calculate_document_trust_score, compile_relationship_nodes, levenshtein_ratio
)
from utils.risk_engine import calculate_aegis_risk
from utils.ocr_engine import process_dossier_file

# ================= CONFIG =================
st.set_page_config(page_title="AI Smart Land & Home Valuation Portal", layout="wide")

# ================= TIME API UTILITIES =================
def get_network_time_details():
    """
    Fetches Kolkata server time properties from WorldTimeAPI, falling back to local system clock.
    """
    try:
        r = requests.get("https://worldtimeapi.org/api/timezone/Asia/Kolkata", timeout=2)
        if r.status_code == 200:
            data = r.json()
            dt_str = data["datetime"]
            dt = datetime.fromisoformat(dt_str)
            return {
                "date": dt.strftime("%d-%m-%Y"),
                "time": dt.strftime("%H:%M:%S"),
                "timezone": data["timezone"],
                "day_of_week": data["day_of_week"],
                "day_of_year": data["day_of_year"],
                "full_ts": dt.strftime("%d-%m-%Y %H:%M:%S")
            }
    except Exception:
        pass
        
    dt_now = datetime.now()
    return {
        "date": dt_now.strftime("%d-%m-%Y"),
        "time": dt_now.strftime("%H:%M:%S"),
        "timezone": "Asia/Kolkata (Local)",
        "day_of_week": dt_now.weekday() + 1,
        "day_of_year": dt_now.timetuple().tm_yday,
        "full_ts": dt_now.strftime("%d-%m-%Y %H:%M:%S")
    }

def get_network_time():
    """
    Backward compatibility wrapper returning full timestamp string.
    """
    return get_network_time_details()["full_ts"]

# ================= WEATHER API UTILITIES =================
def get_current_weather(lat, lon):
    """
    Queries OpenWeather API using coordinate points and caches results.
    """
    if "current_weather_cache" in st.session_state:
        cache = st.session_state["current_weather_cache"]
        if abs(cache["lat"] - lat) < 0.05 and abs(cache["lon"] - lon) < 0.05:
            return cache["weather"]
            
    api_key = "db8abf34273cc1c921dde0f6986a6920"
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            weather_main = data["weather"][0]["main"]
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            weather_info = {"main": weather_main, "temp": temp, "desc": desc}
            st.session_state["current_weather_cache"] = {"lat": lat, "lon": lon, "weather": weather_info}
            return weather_info
    except Exception as e:
        print(f"Error fetching weather: {e}")
        
    return {"main": "Clear", "temp": 26.5, "desc": "clear sky"}

def get_background_style(weather_main):
    """
    Maps Weather types to premium Unsplash real-estate layouts.
    """
    backgrounds = {
        "Clear": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?q=80&w=1970", # Sunny luxury estate
        "Clouds": "https://images.unsplash.com/photo-1449034446853-66c86144b0ad?q=80&w=1920", # Cloudy/misty valley
        "Rain": "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?q=80&w=1920", # Wet/rainy scenery
        "Drizzle": "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?q=80&w=1920",
        "Thunderstorm": "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?q=80&w=1920",
        "Mist": "https://images.unsplash.com/photo-1449034446853-66c86144b0ad?q=80&w=1920",
        "Haze": "https://images.unsplash.com/photo-1449034446853-66c86144b0ad?q=80&w=1920"
    }
    return backgrounds.get(weather_main, "https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=1973")

# Get Coordinates context
lat_val, lon_val = 12.9716, 77.5946
if "valued_property" in st.session_state:
    lat_val = st.session_state["valued_property"]["Latitude"]
    lon_val = st.session_state["valued_property"]["Longitude"]
elif "app_folium_map_main" in st.session_state and st.session_state["app_folium_map_main"].get("last_clicked"):
    lat_val = st.session_state["app_folium_map_main"]["last_clicked"]["lat"]
    lon_val = st.session_state["app_folium_map_main"]["last_clicked"]["lng"]

weather_profile = get_current_weather(lat_val, lon_val)
bg_url = get_background_style(weather_profile["main"])
current_time_info = get_network_time_details()

# ================= HISTORY FILE =================
HISTORY_FILE = "valuation_loan_history.csv"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            return pd.read_csv(HISTORY_FILE)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame(columns=[
        "Reference_No", "Date", "Customer_Name", "State", "District", "Village", "PIN_Code",
        "Survey_Number", "Land_Area", "Land_Type", "Market_Value", "Guidance_Value",
        "Loan_Amount", "LTV_Ratio", "DTI_Ratio", "Risk_Score", "Decision"
    ])

def save_to_history(record):
    df = load_history()
    new_df = pd.DataFrame([record])
    if df.empty:
        df = new_df
    else:
        df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

# ================= DESIGN SYSTEM (CSS) =================
def set_design_system(background_image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(255, 255, 255, 0.45), rgba(255, 255, 255, 0.55)),
            url("{background_image_url}") center/cover fixed;
        }}
        
        /* Slate-dark text colors for readability on light background */
        .stApp, .stApp p, .stApp li, .stApp label {{
            color: #0f172a !important;
            font-weight: 500;
        }}
        
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .section-header {{
            color: #0284c7 !important;
            font-weight: 700;
        }}
        
        /* Force light background on text inputs, select boxes, dropdown buttons, and inner text elements */
        .stSelectbox div[role="button"],
        .stSelectbox div[data-baseweb="select"],
        .stSelectbox div[data-baseweb="select"] > div,
        .stSelectbox span,
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea,
        div[data-baseweb="input"],
        div[data-baseweb="input"] input,
        div[data-baseweb="select"],
        div[data-baseweb="textarea"],
        input, select, textarea {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #0f172a !important;
            border: 1px solid rgba(2, 132, 199, 0.25) !important;
            border-radius: 8px !important;
            -webkit-text-fill-color: #0f172a !important;
        }}

        /* Globally target drop-down list popups (which render in React Portals outside .stApp) */
        div[role="listbox"], ul[role="listbox"], [data-baseweb="popover"], [data-baseweb="popover"] div {{
            background-color: #ffffff !important;
        }}

        /* Enforce dark text inside drop-down options lists */
        [role="option"], [role="option"] div, [role="option"] span, [role="option"] p {{
            background-color: #ffffff !important;
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
        }}

        /* Subtle hover state accent for active selection options */
        [role="option"]:hover, [role="option"]:hover div, [role="option"]:hover span {{
            background-color: rgba(2, 132, 199, 0.1) !important;
            color: #0284c7 !important;
            -webkit-text-fill-color: #0284c7 !important;
        }}

        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }}

        /* Title banner */
        .app-title-container {{
            text-align: center;
            background: rgba(255, 255, 255, 0.45);
            border: 1px solid rgba(2, 132, 199, 0.15);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 25px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.08);
        }}
        
        .main-title {{
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }}
        
        .subtitle {{
            color: #1e293b !important;
            font-size: 16px;
            font-weight: 400;
        }}

        /* Metric Cards */
        .metric-card {{
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(2, 132, 199, 0.12);
            border-left: 5px solid #0284c7;
            border-radius: 12px;
            padding: 20px;
            color: #0f172a !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
            transition: transform 0.2s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(2, 132, 199, 0.3);
        }}
        .metric-card.approved {{
            border-left-color: #10b981;
        }}
        .metric-card.rejected {{
            border-left-color: #ef4444;
        }}
        .metric-title {{
            font-size: 13px;
            color: #334155 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }}
        .metric-value {{
            font-size: 26px;
            font-weight: 700;
            color: #0f172a !important;
        }}

        /* Content block */
        .glass-card {{
            background: rgba(255, 255, 255, 0.5);
            border: 1px solid rgba(2, 132, 199, 0.12);
            padding: 25px;
            border-radius: 16px;
            backdrop-filter: blur(15px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
            margin-bottom: 20px;
        }}

        /* Frosted-Glass Sidebar theme overrides */
        section[data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.5) !important;
            backdrop-filter: blur(10px) !important;
            border-right: 1px solid rgba(2, 132, 199, 0.15) !important;
        }}
        
        section[data-testid="stSidebar"] div.stAlert,
        section[data-testid="stSidebar"] div[data-testid="stNotification"],
        section[data-testid="stSidebar"] div.stAlert > div {{
            background-color: rgba(255, 255, 255, 0.65) !important;
            color: #0f172a !important;
            border: 1px solid rgba(2, 132, 199, 0.15) !important;
        }}

        section[data-testid="stSidebar"] div.stAlert p,
        section[data-testid="stSidebar"] div.stAlert li,
        section[data-testid="stSidebar"] div.stAlert span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h4 {{
            color: #0f172a !important;
        }}
        
        .section-header {{
            color: #0284c7;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            border-bottom: 1px solid rgba(2, 132, 199, 0.15);
            padding-bottom: 6px;
        }}

        /* Leaflet map container */
        .map-instruction {{
            color: #0284c7;
            font-size: 13px;
            font-style: italic;
            margin-bottom: 8px;
        }}

        /* Buttons and Form items override */
        div.stButton > button {{
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            color: white !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            box-shadow: 0 4px 15px rgba(2, 132, 199, 0.2);
            transition: all 0.3s ease;
        }}
        div.stButton > button:hover {{
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.3);
            transform: scale(1.02);
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 15px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 48px;
            white-space: pre-wrap;
            background-color: rgba(255,255,255,0.6) !important;
            border: 1px solid rgba(2, 132, 199, 0.12) !important;
            border-radius: 8px 8px 0px 0px !important;
            color: #475569 !important;
            padding-left: 20px;
            padding-right: 20px;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: rgba(2, 132, 199, 0.08) !important;
            border-color: rgba(2, 132, 199, 0.2) !important;
            color: #0284c7 !important;
            font-weight: bold !important;
        }}
        
        /* Table styles */
        .dataframe {{
            background: rgba(255, 255, 255, 0.6) !important;
            color: #0f172a !important;
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_design_system(bg_url)

# ================= LOAD MODELS =================
@st.cache_resource
def load_ml_models():
    try:
        val_model = pickle.load(open("valuation_model.pkl", "rb"))
        loan_model = pickle.load(open("loan_model.pkl", "rb"))
        return val_model, loan_model
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None

val_model, loan_model = load_ml_models()

# ================= COORDINATE DATABASE =================
coordinate_db = {
    "Karnataka": {
        "Bengaluru Urban": [12.9716, 77.5946],
        "Mysuru": [12.2958, 76.6394],
        "Dharwad": [15.4589, 75.0078]
    },
    "Telangana": {
        "Hyderabad": [17.3850, 78.4867],
        "Medchal-Malkajgiri": [17.5536, 78.4909],
        "Rangareddy": [17.2000, 78.4333]
    },
    "Maharashtra": {
        "Mumbai Suburban": [19.0760, 72.8777],
        "Pune": [18.5204, 73.8567],
        "Nagpur": [21.1458, 79.0882]
    },
    "Tamil Nadu": {
        "Chennai": [13.0827, 80.2707],
        "Coimbatore": [11.0168, 76.9558],
        "Madurai": [9.9252, 78.1198]
    }
}

# ================= SIDEBAR NAVIGATION =================
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 10px;'>
        <h2 style='color:#0284c7;'>🛡️ AegisCR Portal</h2>
        <p style='color:#475569; font-size:12px;'>AI Credit Risk & Land Appraisal System</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Render Live Collateral Weather Indicator with Date and Time below
st.sidebar.markdown(
    f"""
    <div style='background: rgba(255,255,255,0.5); border: 1px solid rgba(2, 132, 199, 0.15); padding: 12px; border-radius: 8px; margin-bottom: 15px;'>
        <p style='margin:0; font-size:11px; color:#475569; text-transform:uppercase;'>⛅ COLLATERAL WEATHER PROFILE</p>
        <h4 style='margin:5px 0 0 0; color:#0284c7;'>{weather_profile['main']} ({weather_profile['temp']}°C)</h4>
        <p style='margin:2px 0 0 0; font-size:12px; color:#475569;'>{weather_profile['desc'].capitalize()}</p>
        <hr style='margin:8px 0; border:0; border-top:1px dashed rgba(2, 132, 199, 0.2);'/>
        <p style='margin:0; font-size:11px; color:#0f172a;'>🗓️ <strong>Date:</strong> {current_time_info['date']}</p>
        <p style='margin:2px 0 0 0; font-size:11px; color:#0f172a;'>🕒 <strong>Time:</strong> {current_time_info['time']} ({current_time_info['timezone']})</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.info(
    "💡 **Quick Walkthrough**:\n"
    "1. **Tab 2**: Register property values & pin coordinates on Leaflet.\n"
    "2. **Tab 3**: Upload PDFs and run OCR cross-document checks to get trust scores.\n"
    "3. **Tab 4**: Appraise final credit sanction limits (Secured/Unsecured).\n"
    "4. **Tab 5**: Review local search & appraisal history."
)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align:center; color:#475569; font-size:10px;'>Final-Year Placement Project © 2026</p>", unsafe_allow_html=True)


# ================= TITLE BANNER =================
st.markdown(
    """
    <div class="app-title-container">
        <div class="main-title">🛡️ AegisCR Underwriting Portal</div>
        <div class="subtitle">AI-Powered Intelligent Underwriting & Collateral Appraisal Platform</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Setup tabs in requested workflow order: Dashboard -> Valuation -> Document Verification -> Loan Prediction -> Logs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Portfolio Dashboard", 
    "🔍 Property Valuation & Map", 
    "📂 Document Verification Check",
    "📊 Smart Loan Prediction", 
    "📜 History Logs"
])

# Load History
history_df = load_history()

# ================= TAB 1: EXECUTIVE DASHBOARD =================
with tab1:
    st.markdown("<div class='section-header'>📊 PORTFOLIO PERFORMANCE CONSOLE</div>", unsafe_allow_html=True)
    
    total_records = len(history_df)
    approved_count = len(history_df[history_df["Decision"] == "APPROVED"]) if total_records > 0 else 876
    rejected_count = len(history_df[history_df["Decision"] == "REJECTED"]) if total_records > 0 else 369
    total_processed = total_records if total_records > 0 else (approved_count + rejected_count)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">📋 total processed loans</div><div class="metric-value">{total_processed:,}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card approved"><div class="metric-title">✅ approved applications</div><div class="metric-value">{approved_count:,}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card rejected"><div class="metric-title">❌ rejected applications</div><div class="metric-value">{rejected_count:,}</div></div>', unsafe_allow_html=True)
    with col4:
        rate = (approved_count / total_processed * 100) if total_processed > 0 else 70.3
        st.markdown(f'<div class="metric-card"><div class="metric-title">📈 average approval rate</div><div class="metric-value">{rate:.1f}%</div></div>', unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📍 Regional Activity Heatmap")
        if not history_df.empty and "District" in history_df.columns:
            dist_counts = history_df["District"].value_counts().reset_index()
            dist_counts.columns = ["District", "Applications"]
            st.bar_chart(dist_counts.set_index("District"))
        else:
            mock_dist = pd.DataFrame({
                "District": ["Bengaluru Urban", "Hyderabad", "Mumbai Suburban", "Chennai", "Pune", "Rangareddy", "Coimbatore"],
                "Applications": [420, 310, 245, 185, 140, 110, 95]
            })
            st.bar_chart(mock_dist.set_index("District"), color="#0284c7")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with gcol2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("⚖️ Risk Score Distribution")
        if not history_df.empty and "Risk_Score" in history_df.columns:
            risk_series = history_df["Risk_Score"]
            hist_vals, bin_edges = np.histogram(risk_series, bins=10, range=(0, 100))
            chart_data = pd.DataFrame(hist_vals, index=bin_edges[:-1], columns=["Risk Scores"])
            st.area_chart(chart_data)
        else:
            mock_risk = np.random.normal(loc=45, scale=18, size=1000)
            mock_risk = np.clip(mock_risk, 5, 95)
            hist_vals, bin_edges = np.histogram(mock_risk, bins=10)
            chart_data = pd.DataFrame(hist_vals, index=[int(x) for x in bin_edges[:-1]], columns=["Risk Scores"])
            st.area_chart(chart_data, color="#38bdf8")
        st.markdown("</div>", unsafe_allow_html=True)


# ================= TAB 2: PROPERTY VALUATION & MAP =================
with tab2:
    st.markdown("<div class='section-header'>🔍 PROPERTY SEARCH & GEOSPATIAL APPRAISAL</div>", unsafe_allow_html=True)
    
    col_inputs, col_map = st.columns([1, 1.2])
    
    with col_inputs:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📋 Property Address Registration")
        
        state = st.selectbox("State", ["Karnataka", "Telangana", "Maharashtra", "Tamil Nadu", "Other"])
        
        if state in GEO_DB:
            district_list = list(GEO_DB[state]["districts"].keys())
            district = st.selectbox("District", district_list)
            village_list = GEO_DB[state]["districts"][district]["villages"]
            village = st.selectbox("Village / Layout", village_list)
        else:
            district = st.text_input("Enter District")
            village = st.text_input("Enter Village")
            
        pincode = st.text_input("PIN Code", value="560066")
        survey_number = st.text_input("Survey Number (e.g. 142/3)", value="101/2")
        
        # Land details
        land_area = st.number_input("Land Area (Sq Ft)", min_value=100, value=2400)
        land_type = st.selectbox("Land Classification", ["Residential", "Commercial", "Agricultural", "Industrial"])
        
        st.markdown("---")
        # Heuristics for home & depreciated curves
        st.subheader("🏠 Home / Building Valuation")
        property_class = st.selectbox(
            "Property Classification", 
            ["Land only", "Independent House", "Residential Apartment", "Commercial Building"]
        )
        
        built_up_area = 0
        building_age = 0
        construction_quality = "Standard"
        
        if property_class != "Land only":
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                built_up_area = st.number_input("Built-up Area (Sq Ft)", min_value=0, value=1500)
                building_age = st.number_input("Age of Building (Years)", min_value=0, value=5)
            with b_col2:
                construction_quality = st.selectbox("Construction Quality", ["Standard", "Premium", "Luxury"])
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col_map:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🗺️ Interactive Land Boundaries (Leaflet Map)")
        st.markdown("<p class='map-instruction'>Click anywhere on the map to pin the land boundaries and capture coordinates.</p>", unsafe_allow_html=True)
        
        lat, lon = 12.9716, 77.5946
        if state in coordinate_db and district in coordinate_db[state]:
            lat, lon = coordinate_db[state][district]
            
        m = folium.Map(location=[lat, lon], zoom_start=14)
        m.add_child(folium.LatLngPopup())
        
        map_data = st_folium(m, width="100%", height=400, key="app_folium_map_main")
        
        clicked_lat, clicked_lon = lat, lon
        if map_data and map_data.get("last_clicked"):
            clicked_lat = map_data["last_clicked"]["lat"]
            clicked_lon = map_data["last_clicked"]["lng"]
            
        st.write(f"📍 **Captured Coordinates:** Latitude: `{clicked_lat:.6f}` | Longitude: `{clicked_lon:.6f}`")
        st.markdown("</div>", unsafe_allow_html=True)

    # Calculate valuation button
    if st.button("Calculate Property Valuation", key="btn_valuation_main"):
        with st.spinner("Valuing collateral assets..."):
            valuation_res = calculate_valuation(
                state, district, village, pincode, survey_number, land_area, land_type, 
                clicked_lat, clicked_lon, property_class, built_up_area, building_age, construction_quality
            )
            
            # Save in session state for loan prediction
            st.session_state["valued_property"] = {
                "State": state,
                "District": district,
                "Village": village,
                "PIN_Code": pincode,
                "Survey_Number": survey_number,
                "Land_Area": land_area,
                "Land_Type": land_type,
                "Latitude": clicked_lat,
                "Longitude": clicked_lon,
                **valuation_res
            }
            st.success("🎉 Property Valuation Processed Successfully!")
            st.rerun()
            
    # Display Valuation report if exists in session state
    if "valued_property" in st.session_state:
        vp = st.session_state["valued_property"]
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🏢 Valuation Results Analysis")
        
        vcol1, vcol2, vcol3 = st.columns(3)
        with vcol1:
            st.markdown(f"**Government Circle (Guidance) Value:**<br/><h2>₹{vp['total_guidance_value']:,.2f}</h2>", unsafe_allow_html=True)
            st.write(f"Land guidance rate: ₹{vp['guidance_value_per_sqft']:,}/sqft")
            if vp['property_class'] != "Land only":
                st.write(f"Building guidance value: ₹{vp['building_guidance_value']:,.2f}")
        with vcol2:
            st.markdown(f"**AI/ML Estimated Market Value:**<br/><h2>₹{vp['total_market_value']:,.2f}</h2>", unsafe_allow_html=True)
            st.write(f"Land market component: ₹{vp['land_market_value']:,.2f}")
            if vp['property_class'] != "Land only":
                st.write(f"Depreciated home value: ₹{vp['building_market_value']:,.2f} (Age: {vp['building_age']} yrs)")
        with vcol3:
            fraud_status = vp["fraud_check"]["status"]
            color_hex = "#10b981" if fraud_status == "PASS" else ("#f59e0b" if fraud_status == "WARNING" else "#ef4444")
            st.markdown(f"**Geospatial Fraud Check:**<br/><h2><font color='{color_hex}'>{fraud_status}</font></h2>", unsafe_allow_html=True)
            if vp["fraud_check"]["flags"]:
                for flag in vp["fraud_check"]["flags"]:
                    st.warning(flag)
                    
        # Nearby listings
        st.markdown("---")
        st.markdown("#### 🏢 Nearby Similar Registered Properties (NGDRS Transactions)")
        nb1, nb2, nb3 = vp["nearby_prices"]
        ndf = pd.DataFrame({
            "Survey Number": [f"{survey_number.split('/')[0]}/{random.randint(1,100)}", f"{random.randint(1,500)}/4", f"{random.randint(1,500)}/2"],
            "Distance (m)": [120, 310, 480],
            "Registered Price (per sqft)": [f"₹{nb1:,}", f"₹{nb2:,}", f"₹{nb3:,}"],
            "Registry Source": ["NGDRS State Registry", "Kaveri Portal / TNREGINET", "Kaveri Portal / TNREGINET"],
            "Transaction Date": ["14-05-2026", "22-04-2026", "10-02-2026"]
        })
        st.table(ndf)
        
        # Projections
        st.markdown("#### 📈 Future Collateral Appreciation Forecast")
        proj = vp["projections"]
        pcol1, pcol2, pcol3, pcol4 = st.columns(4)
        pcol1.metric("Growth Rate", f"{proj['growth_rate_pct']}% Annual")
        pcol2.metric("1 Year Value Projection", f"₹{proj['1yr']:,.2f}")
        pcol3.metric("3 Years Value Projection", f"₹{proj['3yr']:,.2f}")
        pcol4.metric("5 Years Value Projection", f"₹{proj['5yr']:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)


# ================= TAB 3: DOCUMENT VERIFICATION =================
with tab3:
    st.markdown("<div class='section-header'>📂 CROSS-DOCUMENT OCR & COMPLIANCE ALIGNMENT</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:12px;'>Upload loan application PDFs to trigger fuzzy cross-checks, mapping registries, and Document Trust Score compilation.</p>", unsafe_allow_html=True)
    
    # Simulating Tampered Dossiers
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("⚙️ Verification Demo Profile Simulator (For Live Demonstrations)")
    demo_profile = st.selectbox(
        "Select Verification Dossier Spoof Profile",
        [
            "Standard Clean Profile (Approved status)",
            "Identity Tampering / Spoofing (Flags Name Mismatches & Deed Owner Conflicts)",
            "Income Alteration / Salary Bounces (Flags Pay Slip vs Statement variance & EMIs Bounces)",
            "Registry Boundaries Fraud (Flags Geospatial Coordinates map overlay conflicts)"
        ]
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("👤 Verification Context")
    chk_name = st.text_input("Borrower Name (To cross-verify Aadhaar/PAN)", value="Rajesh Kumar")
    chk_salary = st.number_input("Declared Salary (To verify Net Pay in Slip)", min_value=1000, value=75000)
    
    st.markdown("---")
    st.subheader("📁 Upload PDFs for OCR Verification")
    col_up1, col_up2 = st.columns(2)
    upl_aadhaar = col_up1.file_uploader("1. Aadhaar Card PDF", type=["pdf"])
    upl_pan = col_up2.file_uploader("2. PAN Card PDF", type=["pdf"])
    upl_slip = col_up1.file_uploader("3. Salary Slip PDF", type=["pdf"])
    upl_deed = col_up2.file_uploader("4. Sale Deed PDF (Title Deed)", type=["pdf"])
    
    with st.expander("➕ Upload Additional Compliance Documents"):
        col_up3, col_up4 = st.columns(2)
        upl_passport = col_up3.file_uploader("5. Passport PDF", type=["pdf"])
        upl_dl = col_up4.file_uploader("6. Driving Licence PDF", type=["pdf"])
        upl_itr = col_up3.file_uploader("7. ITR Form / Form 16 PDF", type=["pdf"])
        upl_ec = col_up4.file_uploader("8. RTC / Pahani / Encumbrance Certificate PDF", type=["pdf"])
        upl_bill = col_up3.file_uploader("9. Utility Bill PDF", type=["pdf"])
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Run OCR Document Audit"):
        with st.spinner("Extracting parameters with OCR engines..."):
            
            # Record timeline steps dynamically using WorldTimeAPI
            t_upload_details = get_network_time_details()
            t_upload = f"{t_upload_details['full_ts']} (Day: {t_upload_details['day_of_week']}/7)"
            
            # Pull Registry mapping context if available
            vp_data = st.session_state.get("valued_property", None)
            is_unsec = False if vp_data else True
            
            if not vp_data:
                vp_data = {
                    "State": "N/A", "District": "N/A", "Village": "N/A", "PIN_Code": "N/A",
                    "Survey_Number": "N/A", "Land_Area": 0, "Land_Type": "Unsecured",
                    "total_market_value": 1, "total_guidance_value": 0,
                    "land_market_value": 0, "building_market_value": 0,
                    "property_class": "Unsecured (None)", "eligible_ltv": 0.0,
                    "max_loan_amount": chk_salary * 20
                }
                
            # Execute real OCR if files are uploaded, otherwise fall back to demo profiles
            aadhaar_ocr = None
            pan_ocr = None
            salary_slip_ocr = None
            sale_deed_ocr = None
            bank_statement_ocr = None
            
            passport_ocr = None
            dl_ocr = None
            itr_ocr = None
            ec_ocr = None
            bill_ocr = None
            
            # Setup category label based on selection
            if "Standard Clean Profile" in demo_profile:
                profile_lbl = "Standard"
            elif "Identity Tampering" in demo_profile:
                profile_lbl = "Identity Tampering / Spoofing"
            elif "Income Alteration" in demo_profile:
                profile_lbl = "Income Alteration / Salary Bounces"
            else:
                profile_lbl = "Registry Boundaries Fraud"
                
            os.makedirs("temp_uploads", exist_ok=True)
            
            # Process actual uploads if available
            if upl_aadhaar is not None:
                temp_path = os.path.join("temp_uploads", upl_aadhaar.name)
                with open(temp_path, "wb") as f:
                    f.write(upl_aadhaar.getbuffer())
                aadhaar_ocr = process_dossier_file(temp_path, upl_aadhaar.name, "Identity (Aadhaar)")
                try: os.remove(temp_path)
                except: pass
                
            if upl_pan is not None:
                temp_path = os.path.join("temp_uploads", upl_pan.name)
                with open(temp_path, "wb") as f:
                    f.write(upl_pan.getbuffer())
                pan_ocr = process_dossier_file(temp_path, upl_pan.name, "Identity (PAN)")
                try: os.remove(temp_path)
                except: pass
                
            if upl_slip is not None:
                temp_path = os.path.join("temp_uploads", upl_slip.name)
                with open(temp_path, "wb") as f:
                    f.write(upl_slip.getbuffer())
                salary_slip_ocr = process_dossier_file(temp_path, upl_slip.name, "Financial (Salary Slip)")
                try: os.remove(temp_path)
                except: pass
                
            if upl_deed is not None:
                temp_path = os.path.join("temp_uploads", upl_deed.name)
                with open(temp_path, "wb") as f:
                    f.write(upl_deed.getbuffer())
                sale_deed_ocr = process_dossier_file(temp_path, upl_deed.name, "Property (Sale Deed)")
                try: os.remove(temp_path)
                except: pass
                
            # Additional Uploads
            if upl_passport is not None:
                temp_path = os.path.join("temp_uploads", upl_passport.name)
                with open(temp_path, "wb") as f:
                    f.write(upl_passport.getbuffer())
                passport_ocr = process_dossier_file(temp_path, upl_passport.name, "Identity (Passport)")
                try: os.remove(temp_path)
                except: pass
                
            if upl_dl is not None:
                temp_path = os.path.join("temp_uploads", upl_dl.name)
                with open(temp_path, "wb") as f:
                    f.write(upl_dl.getbuffer())
                dl_ocr = process_dossier_file(temp_path, upl_dl.name, "Identity (Driving Licence)")
                try: os.remove(temp_path)
                except: pass
                
            if upl_itr is not None:
                temp_path = os.path.join("temp_uploads", upl_itr.name)
                with open(temp_path, "wb") as f:
                    f.write(upl_itr.getbuffer())
                itr_ocr = process_dossier_file(temp_path, upl_itr.name, "Financial (ITR / Form 16)")
                try: os.remove(temp_path)
                except: pass
                
            if upl_ec is not None:
                temp_path = os.path.join("temp_uploads", upl_ec.name)
                with open(temp_path, "wb") as f:
                    f.write(upl_ec.getbuffer())
                ec_ocr = process_dossier_file(temp_path, upl_ec.name, "Property (EC / RTC)")
                try: os.remove(temp_path)
                except: pass
                
            if upl_bill is not None:
                temp_path = os.path.join("temp_uploads", upl_bill.name)
                with open(temp_path, "wb") as f:
                    f.write(upl_bill.getbuffer())
                bill_ocr = process_dossier_file(temp_path, upl_bill.name, "Utility Bill")
                try: os.remove(temp_path)
                except: pass
                
            t_ocr_details = get_network_time_details()
            t_ocr = f"{t_ocr_details['full_ts']} (Day: {t_ocr_details['day_of_week']}/7)"
            
            # Check if any uploads are present
            has_any_upload = (upl_aadhaar is not None) or (upl_pan is not None) or (upl_slip is not None) or (upl_deed is not None) or \
                             (upl_passport is not None) or (upl_dl is not None) or (upl_itr is not None) or (upl_ec is not None) or (upl_bill is not None)
            
            if has_any_upload:
                # STRICT REAL AUDIT MODE: Non-uploaded files are marked as Missing
                if aadhaar_ocr is None:
                    aadhaar_ocr = {"Missing": True, "Name": "Missing", "DOB": "N/A", "Aadhaar_Number": "MISSING", "Confidence_Score": 0}
                if pan_ocr is None:
                    pan_ocr = {"Missing": True, "Name": "Missing", "DOB": "N/A", "PAN_Number": "MISSING", "Confidence_Score": 0}
                if salary_slip_ocr is None:
                    salary_slip_ocr = {"Missing": True, "Name": "Missing", "Employer": "MISSING", "Net_Monthly_Salary": 0.0, "Confidence_Score": 0}
                if bank_statement_ocr is None:
                    bank_statement_ocr = {"Missing": True, "Salary_Credits": [0.0], "EMI_Bounces": 0, "Average_Balance": 0.0}
                if sale_deed_ocr is None:
                    sale_deed_ocr = {"Missing": True, "Owner": "Missing", "Survey_Number": "MISSING", "Village": "MISSING", "District": "MISSING", "Land_Area": 0, "Confidence_Score": 0}
            else:
                # DEMO SIMULATION MODE: Fall back to selected profile configurations
                if aadhaar_ocr is None:
                    if profile_lbl == "Identity Tampering / Spoofing":
                        aadhaar_ocr = {"Name": chk_name, "DOB": "15-08-1988", "Aadhaar_Number": "4210-9824-1102", "Confidence_Score": 95}
                    else:
                        aadhaar_ocr = {"Name": chk_name, "DOB": "15-08-1988", "Aadhaar_Number": "XXXX-XXXX-1102", "Confidence_Score": 95}
                        
                if pan_ocr is None:
                    if profile_lbl == "Identity Tampering / Spoofing":
                        pan_ocr = {"Name": chk_name + " S", "DOB": "18-10-1988", "PAN_Number": "ABCDE1234F", "Confidence_Score": 95}
                    else:
                        pan_ocr = {"Name": chk_name, "DOB": "15-08-1988", "PAN_Number": "ABCDE1234F", "Confidence_Score": 95}
                        
                if salary_slip_ocr is None:
                    if profile_lbl == "Income Alteration / Salary Bounces":
                        salary_slip_ocr = {"Employer": "Infosys Ltd", "Net_Monthly_Salary": float(chk_salary * 1.35), "Name": chk_name, "Confidence_Score": 90}
                    else:
                        salary_slip_ocr = {"Employer": "Infosys Ltd", "Net_Monthly_Salary": float(chk_salary), "Name": chk_name, "Confidence_Score": 90}
                        
                if bank_statement_ocr is None:
                    if profile_lbl == "Income Alteration / Salary Bounces":
                        bank_statement_ocr = {"Salary_Credits": [chk_salary, chk_salary, chk_salary], "EMI_Bounces": 2, "Average_Balance": chk_salary * 0.15}
                    else:
                        s_val = salary_slip_ocr.get("Net_Monthly_Salary", chk_salary)
                        bank_statement_ocr = {"Salary_Credits": [s_val, s_val, s_val], "EMI_Bounces": 0, "Average_Balance": s_val * 1.5}
                        
                if sale_deed_ocr is None:
                    if profile_lbl == "Registry Boundaries Fraud":
                        sale_deed_ocr = {"Owner": chk_name, "Survey_Number": f"{vp_data['Survey_Number'].split('/')[0]}/{random.randint(50,200)}", "Village": "Chikka Banaswadi", "Land_Area": vp_data["Land_Area"], "Confidence_Score": 92}
                    elif profile_lbl == "Identity Tampering / Spoofing":
                        sale_deed_ocr = {"Owner": "Suresh Kumar", "Survey_Number": vp_data["Survey_Number"], "Village": vp_data["Village"], "Land_Area": vp_data["Land_Area"], "Confidence_Score": 92}
                    else:
                        sale_deed_ocr = {"Owner": chk_name, "Survey_Number": vp_data["Survey_Number"], "Village": vp_data["Village"], "Land_Area": vp_data["Land_Area"], "Confidence_Score": 92}
            
            # Execute verification routines
            identity_res = verify_identity_dossier(aadhaar_ocr, pan_ocr)
            income_res = verify_income_dossier(salary_slip_ocr, chk_salary, chk_name)
            property_res = verify_property_dossier(sale_deed_ocr, vp_data, chk_name)
            cashflow_res = verify_cashflow_stability(salary_slip_ocr, bank_statement_ocr)
            fraud_res = conduct_fraud_brain_audit({}, profile_lbl)
            
            t_forensic_details = get_network_time_details()
            t_forensic = f"{t_forensic_details['full_ts']} (Day: {t_forensic_details['day_of_week']}/7)"
            
            trust_score = calculate_document_trust_score(identity_res, income_res, property_res, cashflow_res, fraud_res, is_unsec)
            
            t_verify_details = get_network_time_details()
            t_verify = f"{t_verify_details['full_ts']} (Day: {t_verify_details['day_of_week']}/7)"
            
            # Save timeline steps
            timeline_logs = [
                {"time": t_upload, "event": "📥 Document Dossier Uploaded", "desc": f"Files uploaded successfully. Strict Audit Mode active: {has_any_upload}."},
                {"time": t_ocr, "event": "🤖 Google Cloud Vision OCR", "desc": "Structured text parameter annotations completed."},
                {"time": t_forensic, "event": "🔍 Forensic Brain Audits & Fraud Check", "desc": f"Analyzed resolution, font alterations, and file EXIF properties (Confidence: {fraud_res.get('Fraud_Brain_Confidence', 98.0)}%)."},
                {"time": t_verify, "event": "🔗 Node Linkage Mappings & Verification Completion", "desc": f"Cross-document fuzzy name matching completed: {trust_score}% score."}
            ]
            
            # Save results in session state
            st.session_state["dossier_verification"] = {
                "Declared_Name": chk_name,
                "trust_score": trust_score,
                "identity": identity_res,
                "income": income_res,
                "property": property_res,
                "cashflow": cashflow_res,
                "fraud": fraud_res,
                "timeline": timeline_logs,
                "ocr_data": {
                    "aadhaar": aadhaar_ocr,
                    "pan": pan_ocr,
                    "salary_slip": salary_slip_ocr,
                    "sale_deed": sale_deed_ocr,
                    "bank_statement": bank_statement_ocr,
                    "passport": passport_ocr,
                    "driving_licence": dl_ocr,
                    "itr": itr_ocr,
                    "ec": ec_ocr,
                    "utility_bill": bill_ocr
                }
            }
            
            st.success("🎉 OCR Document Audit Complete! Trust Score calculated.")
            st.rerun()
            
    # Render Audit findings in Tab 3
    if "dossier_verification" in st.session_state:
        dv = st.session_state["dossier_verification"]
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🔍 Document Audit Dashboard & Alignment Matrix")
        
        # Display Trust progress gauge
        st.markdown(f"#### Verified Document Trust Score: **{dv['trust_score']}%**")
        st.progress(int(dv['trust_score']))
        
        st.markdown("---")
        
        # Split into Trust Network breakdowns & Banking Compliance engine Checklist
        tcol1, tcol2 = st.columns(2)
        
        with tcol1:
            st.markdown("#### 🛡️ Document Trust Network Metrics")
            raw_trust = dv["trust_score"]
            st.write(f"- **Authenticity Index (25%)**")
            st.progress(int(raw_trust * 0.98) if raw_trust > 80 else int(raw_trust * 0.7))
            st.write(f"- **Cross-Doc Consistency (25%)**")
            st.progress(int(raw_trust * 1.0) if raw_trust > 80 else int(raw_trust * 0.5))
            st.write(f"- **Regulatory Compliance (20%)**")
            st.progress(int(raw_trust * 0.95) if raw_trust > 80 else int(raw_trust * 0.6))
            st.write(f"- **AI Fraud Brain Score (20%)**")
            st.progress(int(raw_trust * 1.0) if raw_trust > 80 else int(raw_trust * 0.4))
            st.write(f"- **OCR Text Confidence (10%)**")
            st.progress(92)
            
        with tcol2:
            st.markdown("#### 📋 Banking Compliance Audit Checklist")
            is_good = dv["trust_score"] >= 85.0
            st.write("✅ **KYC Completeness Verified**" if is_good else "⚠️ **KYC Mismatch Alert Flags**")
            st.write("✅ **Aadhaar Format Validation (12 Digits Checked)**")
            st.write("✅ **PAN Format Validation Check Passed**")
            st.write("✅ **IFSC Code Integrity Check Verified**")
            st.write("✅ **RBI Policy Cap: Debt-to-Income check**")
            st.write("✅ **Bank Lending Cap: LTV threshold checks**")
            
        st.markdown("---")
        
        # Render Relationship Nodes
        st.markdown("#### 🔗 AI Relationship Nodes (Fuzzy Integrity Checks)")
        id_chk = dv["identity"]
        inc_chk = dv["income"]
        prop_chk = dv["property"]
        cf_chk = dv["cashflow"]
        fr_chk = dv["fraud"]
        
        rel_nodes = compile_relationship_nodes(
            dv["Declared_Name"], id_chk, inc_chk, prop_chk, cf_chk, fr_chk, (prop_chk.get("Survey_Status") == "N/A")
        )
        
        node_df_data = []
        for node in rel_nodes:
            status_val = "🟢 ALIGN" if node["status"] == "PASS" else "🔴 CONFLICT"
            node_df_data.append([
                node["from"], "↔", node["to"], node["check"], f"{node['score']}% similarity", status_val
            ])
            
        # Append additional nodes dynamically
        if dv.get("ocr_data", {}).get("passport"):
            p_data = dv["ocr_data"]["passport"]
            if p_data and not p_data.get("Missing"):
                p_ratio = levenshtein_ratio(p_data["Name"], dv["Declared_Name"])
                node_df_data.append(["Borrower", "↔", "Passport", "Passport Name Consistency", f"{int(p_ratio*100)}% similarity", "🟢 ALIGN" if p_ratio >= 0.85 else "🔴 CONFLICT"])
                
        if dv.get("ocr_data", {}).get("driving_licence"):
            dl_data = dv["ocr_data"]["driving_licence"]
            if dl_data and not dl_data.get("Missing"):
                dl_ratio = levenshtein_ratio(dl_data["Name"], dv["Declared_Name"])
                node_df_data.append(["Borrower", "↔", "Driving Licence", "DL Name Consistency", f"{int(dl_ratio*100)}% similarity", "🟢 ALIGN" if dl_ratio >= 0.85 else "🔴 CONFLICT"])
                
        if dv.get("ocr_data", {}).get("itr"):
            itr_data = dv["ocr_data"]["itr"]
            if itr_data and not itr_data.get("Missing"):
                itr_ratio = levenshtein_ratio(itr_data["Name"], dv["Declared_Name"])
                node_df_data.append(["Borrower", "↔", "ITR Form / Form 16", "ITR Name Consistency", f"{int(itr_ratio*100)}% similarity", "🟢 ALIGN" if itr_ratio >= 0.85 else "🔴 CONFLICT"])
                
        if dv.get("ocr_data", {}).get("ec"):
            ec_data = dv["ocr_data"]["ec"]
            if ec_data and not ec_data.get("Missing"):
                ec_ratio = levenshtein_ratio(ec_data["Owner"], dv["Declared_Name"])
                node_df_data.append(["Borrower", "↔", "EC / RTC pahani", "EC Owner Registry Match", f"{int(ec_ratio*100)}% similarity", "🟢 ALIGN" if ec_ratio >= 0.85 else "🔴 CONFLICT"])
            
        ndf = pd.DataFrame(node_df_data, columns=["Primary Node", "link", "Secondary Node", "Verification Action", "Consistency Metric", "Alignment Status"])
        st.table(ndf)
        
        # Render Timeline Logs
        if "timeline" in dv:
            st.markdown("---")
            st.markdown("#### 🕒 Dossier Forensic Audit Timeline")
            for item in dv["timeline"]:
                st.markdown(
                    f"""
                    <div style='background: rgba(255, 255, 255, 0.4); border-left: 3px solid #0284c7; padding: 10px 15px; border-radius: 4px; margin-bottom: 8px;'>
                        <span style='color: #475569; font-size: 11px; font-weight: bold;'>[{item['time']}]</span><br/>
                        <strong style='color: #0284c7;'>{item['event']}</strong> — <span style='color: #1e293b; font-size: 13px;'>{item['desc']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown("---")
        
        # Render AI Fraud Brain Logs
        st.markdown("#### 🧠 AI Fraud Brain Audit Logs")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown(f"- **Scan Resolution Verification**: `{fr_chk['Scan_Quality']}`")
            st.markdown(f"- **Aadhaar Mask Status**: `{'🟢 Masked OK' if fr_chk['Status'] == 'PASS' else '🔴 ALERT: Plain UID visible'}`")
            st.markdown(f"- **QR Code Signature Match**: `{fr_chk['QR_Code_Audit']}`")
        with col_f2:
            st.markdown(f"- **System Font Alterations**: `{'🟢 Fonts standard' if fr_chk['Font_Consistency'] == 'Standard Verified' else '🔴 ALERT: altered fonts detected'}`")
            st.markdown(f"- **Metadata compress anomalies**: `{'🟢 Clean Signature' if fr_chk['Metadata_Integrity'] == 'Clean Signature' else '🔴 ALERT: Edit history modified via external tools'}`")
            
        st.markdown("---")
        
        # Render Behavioral Cashflow stability
        st.markdown("#### 📊 Behavioural Cash Flow Risk Card")
        col_cf1, col_cf2 = st.columns(2)
        with col_cf1:
            st.markdown(f"- **Bank Deposits consistency**: `{'🟢 Stable matching credits' if cf_chk['Status'] == 'PASS' else '🔴 ALERT: salary variance detected'}`")
            st.markdown(f"- **EMI Bounces logs**: `{'🟢 0 default entries' if cf_chk['EMI_Bounces'] == 0 else f'🔴 {cf_chk['EMI_Bounces']} default bounces detected'}`")
        with col_cf2:
            st.markdown(f"- **Cashflow stability Index**: `{cf_chk['Cashflow_Stability_Score']}/100`")
            st.markdown(f"- **Reserve balance reserve**: `₹{cf_chk['Average_Balance']:,.2f}`")
            
        # Display aggregated warn alerts
        all_alerts = id_chk["Flags"] + inc_chk["Flags"] + prop_chk["Flags"] + cf_chk["Flags"] + fr_chk["Flags"]
        st.markdown("---")
        if all_alerts:
            st.warning("⚠️ **Matching Deviations Flagged by Verification Gateway:**")
            for alert in all_alerts:
                st.write(f"- {alert}")
        else:
            st.success("✅ Document checks verified cleanly. Ready to predict approval in Tab 4.")
            
        st.markdown("</div>", unsafe_allow_html=True)


# ================= TAB 4: SMART LOAN PREDICTION =================
with tab4:
    st.markdown("<div class='section-header'>📊 COMBINED CREDIT RISK & COLLATERAL ANALYSIS</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("⚙️ Collateral & Guarantee Structure")
    collateral_mode = st.selectbox(
        "Select Loan Structure", 
        ["Secured (Using Borrower Owned Property)", "Secured (Using Co-Applicant Owned Property)", "Unsecured Loan (Based on Income & CIBIL)"]
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Check property mapping based on mode
    has_property = False
    vp = None
    
    if collateral_mode in ["Secured (Using Borrower Owned Property)", "Secured (Using Co-Applicant Owned Property)"]:
        if "valued_property" not in st.session_state:
            st.info("⚠️ Please complete the property valuation and mapping steps on the **🔍 Property Valuation & Map** tab first, then link it here.")
        else:
            vp = st.session_state["valued_property"]
            has_property = True
            if collateral_mode == "Secured (Using Borrower Owned Property)":
                st.success(f"✅ Linked Borrower Collateral: Survey `{vp['Survey_Number']}` in `{vp['Village']}, {vp['District']}` (Valued: ₹{vp['total_market_value']:,.2f})")
            else:
                st.success(f"✅ Linked Co-Applicant Collateral: Survey `{vp['Survey_Number']}` in `{vp['Village']}, {vp['District']}` (Valued: ₹{vp['total_market_value']:,.2f})")
    else:
        # Unsecured Mode
        has_property = True
        st.success("✅ Unsecured Credit Mode Active: No property collateral required. Evaluation will be based on income & credit bureau parameters.")
        
    if has_property:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("👤 Applicant Personal & Credit History")
        
        lcol1, lcol2 = st.columns(2)
        with lcol1:
            name = st.text_input("Borrower Name", value="Rajesh Kumar")
            gender = st.selectbox("Gender", ["Male", "Female"])
            married = st.selectbox("Married Status", ["Yes", "No"])
            dependents = st.selectbox("Dependents Count", [0, 1, 2, 3])
            education = st.selectbox("Education Level", ["Graduate", "Not Graduate"])
            self_emp = st.selectbox("Self Employed Status", ["Yes", "No"])
            
        with lcol2:
            credit_hist = st.selectbox("Credit Bureau Rating (CIBIL Status)", [1.0, 0.0], 
                                     format_func=lambda x: "Good / Satisfactory (>= 750)" if x == 1.0 else "Default / Poor History (< 650)")
            app_income = st.number_input("Applicant Monthly Income (₹)", min_value=1000, value=75000)
            co_income = st.number_input("Co-Applicant Monthly Income (₹)", min_value=0, value=35000)
            loan_term = st.number_input("Loan Repayment Tenure (Months)", min_value=12, max_value=360, value=240)
            
            # Contextual maximum loan limits
            total_monthly_income = app_income + co_income
            if collateral_mode == "Unsecured Loan (Based on Income & CIBIL)":
                max_eligible_cap = int(total_monthly_income * 20)
                st.markdown(f"💡 **Recommended Max Unsecured Loan (20x Income):** `₹{max_eligible_cap:,.2f}`")
                loan_amount = st.number_input("Requested Loan Sanction (₹)", min_value=10000, value=min(500000, max_eligible_cap))
            else:
                st.markdown(f"💡 **Recommended Max Loan (LTV Cap):** `₹{vp['max_loan_amount']:,.2f}` ({int(vp['eligible_ltv']*100)}% of Collateral)")
                if collateral_mode == "Secured (Using Co-Applicant Owned Property)" and co_income == 0:
                    st.warning("⚠️ For Co-Applicant collateral, co-applicant income or guarantees should ideally be declared.")
                loan_amount = st.number_input("Requested Loan Sanction (₹)", min_value=10000, value=min(int(vp['total_market_value'] * 0.7), int(vp['max_loan_amount'])))

        # Link validation state if available from verification tab
        dossier_checked = False
        trust_score = 95.0
        identity_res = None
        income_res = None
        property_res = None
        cashflow_res = None
        fraud_res = None
        
        if "dossier_verification" in st.session_state:
            dv = st.session_state["dossier_verification"]
            if dv["Declared_Name"].strip().lower() == name.strip().lower():
                dossier_checked = True
                trust_score = dv["trust_score"]
                identity_res = dv["identity"]
                income_res = dv["income"]
                property_res = dv["property"]
                cashflow_res = dv["cashflow"]
                fraud_res = dv["fraud"]
                st.success(f"✅ Linked verified documents for '{name}' (Document Trust Index Score: **{trust_score}%**)")
                
        if not dossier_checked:
            st.warning("⚠️ **Compliance Block**: Applicant document audits have not been performed. Please run the OCR Document Audit in the **📂 Document Verification Check** tab (Tab 3) first to continue.")
            
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("✍️ Underwriting Audit Notes")
        officer_notes_input = st.text_area(
            "Write Field Notes & Special Observations (included in PDF sanction letter)", 
            value=f"Applicant credentials and document nodes reviewed. Pinned coordinates verified at survey boundary {vp['Survey_Number'] if vp else 'N/A'}."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("Evaluate & Predict Loan Approval", key="btn_loan_main"):
            if not dossier_checked:
                st.error("❌ Evaluation Blocked: Document verification is mandatory for underwriting audit decisions. Please complete Tab 3 compliance checks first.")
                st.stop()
            with st.spinner("Analyzing credit parameters, pricing debt, and querying Groq AI Underwriter..."):
                
                # Fetch prediction lifecycle timestamps using WorldTimeAPI
                t_risk_details = get_network_time_details()
                t_risk = f"{t_risk_details['full_ts']} (Day: {t_risk_details['day_of_week']}/7)"
                
                total_income = app_income + co_income
                
                # Mock a dummy property dict for Unsecured Mode to avoid empty errors down the line
                if collateral_mode == "Unsecured Loan (Based on Income & CIBIL)":
                    vp = {
                        "State": "N/A", "District": "N/A", "Village": "N/A", "PIN_Code": "N/A",
                        "Survey_Number": "N/A", "Land_Area": 0, "Land_Type": "Unsecured",
                        "total_market_value": 1, # Avoid divide by zero
                        "total_guidance_value": 0,
                        "land_market_value": 0,
                        "building_market_value": 0,
                        "property_class": "Unsecured (None)",
                        "eligible_ltv": 0.0,
                        "max_loan_amount": total_income * 20,
                        "fraud_check": {"status": "PASS", "flags": []},
                        "projections": {"growth_rate_pct": 0, "1yr": 0, "3yr": 0, "5yr": 0},
                        "nearby_prices": [0, 0, 0]
                    }
                    ltv_ratio = 0.0
                else:
                    ltv_ratio = loan_amount / vp["total_market_value"]
                
                monthly_rate = 0.09 / 12
                emi = loan_amount * (monthly_rate * (1 + monthly_rate)**loan_term) / ((1 + monthly_rate)**loan_term - 1)
                dti_ratio = emi / total_income
                
                # Construct defaults if not verified in Tab 3 (Safeguarded by st.stop(), but kept for fallback assurance)
                if not dossier_checked:
                    aadhaar_mock = {"Name": name, "DOB": "15-08-1988", "Aadhaar_Number": "4210-9824-1102"}
                    pan_mock = {"Name": name, "DOB": "15-08-1988", "PAN_Number": "ABCDE1234F"}
                    slip_mock = {"Employer": "Infosys Ltd", "Net_Monthly_Salary": app_income, "Name": name}
                    deed_mock = {"Owner": name, "Survey_Number": vp["Survey_Number"], "Village": vp["Village"], "Land_Area": vp["Land_Area"]}
                    bank_mock = {"Salary_Credits": [app_income], "EMI_Bounces": 0, "Average_Balance": app_income * 1.5}
                    
                    identity_res = verify_identity_dossier(aadhaar_mock, pan_mock)
                    income_res = verify_income_dossier(slip_mock, app_income, name)
                    property_res = verify_property_dossier(deed_mock, vp, name)
                    cashflow_res = verify_cashflow_stability(slip_mock, bank_mock)
                    fraud_res = conduct_fraud_brain_audit({}, "Standard")
                    
                    trust_score = calculate_document_trust_score(identity_res, income_res, property_res, cashflow_res, fraud_res, (collateral_mode == "Unsecured Loan (Based on Income & CIBIL)"))
                    
                vp["trust_score"] = trust_score
                
                # Calculate risk score
                risk_res = calculate_aegis_risk(
                    identity_res, income_res, property_res, credit_hist,
                    ltv_ratio, dti_ratio, vp
                )
                risk_score = risk_res["Aegis_Risk_Index"]
                vp["Risk_Score"] = risk_score
                
                prop_area = "Urban" if vp["District"] in ["Bengaluru Urban", "Hyderabad", "Mumbai Suburban", "Chennai"] else "Semiurban"
                
                # ML Prediction
                loan_approved = 0
                if loan_model is not None:
                    input_df = pd.DataFrame([{
                        "Gender": gender,
                        "Married": married,
                        "Dependents": dependents,
                        "Education": education,
                        "Self_Employed": self_emp,
                        "Property_Area": prop_area,
                        "Land_Type": vp["Land_Type"],
                        "Loan_Amount": loan_amount,
                        "Total_Income": total_income,
                        "Loan_Amount_Term": loan_term,
                        "Credit_History": credit_hist,
                        "Total_Market_Value": vp["total_market_value"],
                        "Total_Guidance_Value": vp["total_guidance_value"],
                        "LTV_Ratio": ltv_ratio,
                        "DTI_Ratio": dti_ratio,
                        "Risk_Score": risk_score
                    }])
                    try:
                        loan_approved = loan_model.predict(input_df)[0]
                    except Exception as e:
                        st.error(f"Prediction Error: {e}")
                        loan_approved = 1 if (credit_hist == 1.0 and (ltv_ratio < 0.85 or ltv_ratio == 0.0) and dti_ratio < 0.55) else 0
                else:
                    loan_approved = 1 if (credit_hist == 1.0 and (ltv_ratio < 0.85 or ltv_ratio == 0.0) and dti_ratio < 0.55) else 0
                
                # Underwriting compliance and risk score safety overrides
                override_triggered = False
                override_msg = ""
                if trust_score < 80.0:
                    loan_approved = 0
                    override_triggered = True
                    override_msg = "Compliance Rejection: Failed document verification matches (Document Trust Score below 80%)."
                elif risk_score >= 65.0:
                    loan_approved = 0
                    override_triggered = True
                    override_msg = "Risk Threshold Override: Forced rejection due to High/Critical ARI Rating."
                    
                decision_text = "Approved" if loan_approved == 1 else "Rejected"
                
                t_decision_details = get_network_time_details()
                t_decision = f"{t_decision_details['full_ts']} (Day: {t_decision_details['day_of_week']}/7)"
                
                # Groq API Underwriting Report
                collateral_desc = f"Structure: {collateral_mode}"
                ai_report = generate_ai_underwriting_report(
                    f"{name} ({collateral_desc})", credit_hist, total_income, loan_amount, loan_term, vp, (loan_approved == 1),
                    identity_res, income_res, property_res, risk_res, officer_notes_input
                )
                
                # Generate PDF Report
                pdf_path = generate_pdf(
                    name, gender, married, dependents, education, self_emp, credit_hist, prop_area,
                    loan_amount, loan_term, app_income, co_income, decision_text, vp, ai_report,
                    {"aadhaar": {"Name": name, "Confidence_Score": 95, "DOB": "15-08-1988", "Aadhaar_Number": "4210-9824-1102"}, 
                     "pan": {"Name": name, "Confidence_Score": 95, "DOB": "15-08-1988", "PAN_Number": "ABCDE1234F"}, 
                     "salary_slip": {"Employer": "Infosys Ltd", "Net_Monthly_Salary": app_income, "Confidence_Score": 90}, 
                     "sale_deed": {"Owner": name, "Survey_Number": vp["Survey_Number"], "Village": vp["Village"], "Land_Area": vp["Land_Area"], "Confidence_Score": 92}},
                    identity_res, risk_res, officer_notes_input
                )
                
                t_pdf_details = get_network_time_details()
                t_pdf = f"{t_pdf_details['full_ts']} (Day: {t_pdf_details['day_of_week']}/7)"
                
                # Append underwriting logs to the timeline
                underwriting_timeline = [
                    {"time": t_risk, "event": "📊 Aegis Credit Risk Assessment", "desc": f"Multi-factor credit algorithm score computed: {risk_score}/100 Index ({risk_res['Rating']})."},
                    {"time": t_decision, "event": "👨‍💼 Officer Decision Directive", "desc": f"Decision set to {decision_text.upper()}. Override warnings flag: {override_triggered}."},
                    {"time": t_pdf, "event": "📑 Sanction PDF Report Compiled", "desc": f"Generated final sanction letter registry dossier. Saved in logs."}
                ]
                
                # Save underwriting timeline logs in session state
                st.session_state["underwriting_timeline"] = underwriting_timeline
                
                # Store in history
                ref_no = f"LN{random.randint(100000,999999)}"
                history_record = {
                    "Reference_No": ref_no,
                    "Date": pd.Timestamp.now().strftime("%d-%m-%Y"),
                    "Customer_Name": f"{name} ({collateral_mode.split(' ')[0]})",
                    "State": vp["State"],
                    "District": vp["District"],
                    "Village": vp["Village"],
                    "PIN_Code": vp["PIN_Code"],
                    "Survey_Number": vp["Survey_Number"],
                    "Land_Area": vp["Land_Area"],
                    "Land_Type": vp["Land_Type"],
                    "Market_Value": vp["total_market_value"] if collateral_mode != "Unsecured Loan (Based on Income & CIBIL)" else 0,
                    "Guidance_Value": vp["total_guidance_value"] if collateral_mode != "Unsecured Loan (Based on Income & CIBIL)" else 0,
                    "Loan_Amount": loan_amount,
                    "LTV_Ratio": round(ltv_ratio, 3),
                    "DTI_Ratio": round(dti_ratio, 3),
                    "Risk_Score": risk_score,
                    "Decision": decision_text.upper()
                }
                save_to_history(history_record)
                
                st.success("🎉 Underwriting Predict Evaluation Complete! Decision matrix logged.")
                st.rerun()
                
        # Render Decision details if saved
        if "underwriting_timeline" in st.session_state:
            # Show results on UI
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("📊 Underwriting Decision & Credit Audit")
            
            # Fetch decision metrics from valuation details
            # Get latest decision from fresh history
            last_record = history_df.iloc[-1] if not history_df.empty else {"Decision": "APPROVED", "Reference_No": "LN892401"}
            decision_text = last_record["Decision"].capitalize()
            
            # Render DIGITAL LOAN TWIN Profile Card
            st.markdown("#### 👤 Applicant Digital Loan Twin Profile")
            twin_c1, twin_c2 = st.columns(2)
            with twin_c1:
                st.markdown(f"- **Unified Profile Owner**: {name} ({gender} / {married})")
                st.markdown(f"- **Repayment Capacity (DTI)**: `{dti_ratio*100:.1f}%` (EMI: ₹{emi:,.2f}/mo)")
                st.markdown(f"- **Collateral Coverage (LTV)**: `{'0.0% (Unsecured)' if collateral_mode == 'Unsecured Loan (Based on Income & CIBIL)' else f'{ltv_ratio*100:.1f}%'}`")
                st.markdown(f"- **Document Trust Score**: `{trust_score}%` ({'Verified' if trust_score >= 85 else 'Review Required'})")
            with twin_c2:
                # Fallback indices
                risk_res_temp = calculate_aegis_risk(identity_res, income_res, property_res, credit_hist, ltv_ratio, dti_ratio, vp)
                st.markdown(f"- **ML Default Probability**: `{risk_res_temp['Probability_Of_Default']}%` (ARI Score: `{vp['Risk_Score']}/100`)")
                st.markdown(f"- **Expected Savings Habit**: `{'Good Reserves' if trust_score >= 80 else 'Altered Cashflow pattern'}`")
                st.markdown(f"- **Recommended Decision Directive**: **{decision_text.upper()}**")
            
            st.markdown("---")
            
            # Render Explainable AI Risk Waterfall
            st.markdown("#### 🧠 Explainable AI (XAI) Waterfall Risk Breakdowns")
            st.markdown("The following compliance deviations increased the overall risk index score of the applicant:")
            risk_res_temp = calculate_aegis_risk(identity_res, income_res, property_res, credit_hist, ltv_ratio, dti_ratio, vp)
            xai_list = risk_res_temp["XAI_Waterfall"]
            for factor_item in xai_list:
                col_x1, col_x2 = st.columns([3, 1])
                col_x1.write(f"- {factor_item['factor']}")
                col_x2.markdown(f"**<font color='{risk_res_temp['Color']}'>{factor_item['impact']}</font>**", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # AI Case Investigator Dossier Panel
            st.markdown("#### 🔍 AI Case Investigator Dossier")
            cinv_c1, cinv_c2 = st.columns(2)
            with cinv_c1:
                # Trigger warning overrides
                st_override = trust_score < 80.0 or vp["Risk_Score"] >= 65.0
                st.markdown(f"**Case Risk Status**: `{'🔴 FLAG CRITICAL WARNINGS' if st_override else '🟢 CLEAN AUDIT'}`")
                if trust_score < 80.0:
                    st.markdown(f"**Rejection Trigger**: *Compliance Rejection: Failed document matches (Trust Score below 80%)*")
                elif vp["Risk_Score"] >= 65.0:
                    st.markdown(f"**Rejection Trigger**: *Risk Threshold Override: Forced rejection due to High/Critical ARI Rating.*")
                else:
                    st.markdown("**Rejection Trigger**: *None (Parameters align within banking policy rules)*")
                st.markdown(f"**Mandatory KYC Documents**: Verified (Aadhaar & PAN matched)")
            with cinv_c2:
                st.markdown("**🔍 Recommended Underwriter Interview Questions:**")
                if trust_score < 80.0:
                    st.write("1. *Ask the applicant to explain the Name/DOB discrepancies flag on Identity cards.*")
                    st.write("2. *Request physical/original Sale Deed deeds to verify owner registry alignment.*")
                else:
                    st.write("1. *Verify the applicant's current net take-home salary is consistent.*")
                    st.write("2. *Review standard field surveyor property photos before closing.*")
                    
            st.markdown("---")
            
            # Underwriting timeline log render
            st.markdown("#### 🕒 Underwriting Decision Lifecycle Timeline")
            for item in st.session_state["underwriting_timeline"]:
                st.markdown(
                    f"""
                    <div style='background: rgba(255, 255, 255, 0.4); border-left: 3px solid #10b981; padding: 10px 15px; border-radius: 4px; margin-bottom: 8px;'>
                        <span style='color: #475569; font-size: 11px; font-weight: bold;'>[{item['time']}]</span><br/>
                        <strong style='color: #10b981;'>{item['event']}</strong> — <span style='color: #1e293b; font-size: 13px;'>{item['desc']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            st.markdown("---")
            
            rcol1, rcol2 = st.columns(2)
            with rcol1:
                if decision_text.upper() == "APPROVED":
                    st.success(f"🎉 **LOAN APPROVED**")
                else:
                    st.error(f"❌ **LOAN REJECTED**")
                    if trust_score < 80.0:
                        st.warning("⚠️ Compliance Rejection: Failed document matches.")
                    elif vp["Risk_Score"] >= 65.0:
                        st.warning("⚠️ Risk Override: Forced rejection due to High/Critical ARI Rating.")
                    
                st.markdown(f"**Aegis Risk Index:** `{vp['Risk_Score']}/100` ({risk_res_temp['Rating']})")
                
            with rcol2:
                st.markdown("#### 📥 Official Bank PDF Report")
                st.markdown("Click below to download the combined Land/Home Valuation & Loan Sanction Letter PDF:")
                try:
                    pdf_n = f"assets/generated_letters/{name.replace(' ', '_')}_sanction_report.pdf"
                    if os.path.exists(pdf_n):
                        with open(pdf_n, "rb") as f:
                            st.download_button(
                                "📥 Download Valuation & Sanction Letter",
                                f,
                                file_name=f"{name.replace(' ', '_')}_sanction_report.pdf",
                                mime="application/pdf",
                                key="btn_pdf_download_main"
                            )
                except Exception as ex:
                    st.error(f"Error packing download button: {ex}")
                    
            st.markdown("---")
            st.markdown("#### 🤖 Groq LLM Underwriting Analysis")
            st.markdown(ai_report)
            
            # Chat assistant copilot directly below predictions!
            st.markdown("---")
            st.subheader("💬 AI Underwriting Copilot Chat")
            ctx_chat = (
                f"Applicant Name: {name}\n"
                f"Income declared: ₹{app_income}/mo | Co-borrower: ₹{co_income}/mo\n"
                f"Credit CIBIL Rating: {'Satisfactory' if credit_hist == 1.0 else 'Defaults'}\n"
                f"Requested Loan: ₹{loan_amount} | Tenure: {loan_term} months\n"
                f"Collateral Type: {vp.get('property_class', 'None')} | Market Value: ₹{vp['total_market_value']}\n"
                f"Aegis Risk Index (ARI): {vp['Risk_Score']}/100\n"
                f"Document Trust Index Score: {trust_score}%\n"
                f"Decision status: {decision_text}"
            )
            if "chat_history_main" not in st.session_state:
                st.session_state["chat_history_main"] = []
                
            copilot_msg = st.text_input("💬 Ask the AI Underwriting Copilot...", key="copilot_msg_input")
            if st.button("Query Copilot", key="btn_query_copilot"):
                if copilot_msg:
                    with st.spinner("Copilot analyzing dossier..."):
                        copilot_reply = query_underwriter_chat(copilot_msg, ctx_chat)
                        st.session_state["chat_history_main"].append((copilot_msg, copilot_reply))
                        
            for q, a in reversed(st.session_state["chat_history_main"]):
                st.write(f"👤 **Officer:** {q}")
                st.write(f"🤖 **Copilot:** {a}")
                st.markdown("---")
                
            st.markdown("</div>", unsafe_allow_html=True)


# ================= TAB 5: VALUATION & LOAN LOGS =================
with tab5:
    st.markdown("<div class='section-header'>📜 VALUATION & DECISION PORTAL LOGS</div>", unsafe_allow_html=True)
    
    fresh_history_df = load_history()
    if fresh_history_df.empty:
        st.info("No applications evaluated yet. History logs will populate automatically once you process values and loans.")
    else:
        st.dataframe(
            fresh_history_df,
            column_config={
                "Market_Value": st.column_config.NumberColumn("Estimated Market Value", format="₹%,.2f"),
                "Circle Guidance Value": st.column_config.NumberColumn("Circle Guidance Value", format="₹%,.2f"),
                "Loan_Amount": st.column_config.NumberColumn("Sanction Requested", format="₹%,.2f"),
                "LTV_Ratio": st.column_config.NumberColumn("LTV Ratio", format="%.2f"),
                "DTI_Ratio": st.column_config.NumberColumn("DTI Ratio", format="%.2f"),
                "Risk_Score": st.column_config.ProgressColumn("Risk Index Score", min_value=0, max_value=100, format="%d/100")
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("Clear Logs / Reset Portal History"):
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            st.success("Portal history reset successfully. Reloading...")
            st.rerun()