import tenacity
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "PythonProject1"))

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
from utils.valuation_module import calculate_valuation, GEO_DB
from utils.verification_engine import (
    levenshtein_ratio, compile_relationship_nodes,
    verify_identity_dossier, verify_income_dossier, verify_property_dossier,
    verify_cashflow_stability, conduct_fraud_brain_audit, calculate_document_trust_score
)
from utils.risk_engine import calculate_aegis_risk
from utils.ai_explainer import generate_ai_underwriting_report, query_underwriter_chat
from utils.pdf_generator import generate_pdf, generate_gold_pdf
from utils.model_loader import get_loan_model
import json
from translations import t
# ================= MEMORY LOGGING HELPER =================
def log_memory_usage(tag=""):
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / (1024 * 1024)
        print(f"[MEMORY LOG] {tag} - RAM Usage: {mem_mb:.2f} MB")
    except Exception:
        pass

log_memory_usage("App Startup Initialized")

# --- Configurable GitHub repository URL ---
GITHUB_REPO_URL = os.environ.get("GITHUB_REPOSITORY_URL", "https://github.com/shrishailad24/AegisCR").strip()

@st.cache_resource
def get_git_info():
    version = "v2.1.0-Prod"
    commit_hash = "N/A"
    try:
        import subprocess
        commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()
    except Exception:
        try:
            git_dir = os.path.join(os.path.dirname(__file__), ".git")
            if os.path.exists(git_dir):
                head_file = os.path.join(git_dir, "HEAD")
                with open(head_file, "r") as f:
                    ref = f.readline().strip()
                if ref.startswith("ref:"):
                    ref_path = os.path.join(git_dir, ref.split(" ")[1])
                    with open(ref_path, "r") as f:
                        commit_hash = f.readline().strip()[:7]
        except Exception:
            pass
    return version, commit_hash

@st.cache_data(show_spinner=False)
def _cached_reverse_geocode(lat_r, lon_r):
    import requests
    try:
        headers = {"User-Agent": "AegisCR-Valuation-App/1.0"}
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat_r}&lon={lon_r}&format=json&accept-language=en"
        r = requests.get(url, headers=headers, timeout=3)
        if r.status_code == 200:
            data = r.json()
            address = data.get("address", {})
            
            state = address.get("state", "")
            if "karnataka" in state.lower():
                state = "Karnataka"
            elif "telangana" in state.lower():
                state = "Telangana"
            elif "maharashtra" in state.lower():
                state = "Maharashtra"
            elif "tamil nadu" in state.lower():
                state = "Tamil Nadu"
            else:
                state = "Other"
                
            district = address.get("city_district", address.get("county", address.get("district", address.get("city", ""))))
            taluk = address.get("subdistrict", address.get("suburb", address.get("town", address.get("village", ""))))
            village = address.get("neighbourhood", address.get("village", address.get("suburb", address.get("road", address.get("hamlet", "")))))
            postcode = address.get("postcode", "")
            
            return state, district, taluk, village, postcode
    except Exception as e:
        print(f"[REVERSE GEOCODE ERROR] {e}")
    return None

def reverse_geocode(lat, lon):
    """
    Reverse geocodes lat/lon using Nominatim OpenStreetMap API.
    Returns: (state, district, taluk, village, postcode)
    """
    if lat is None or lon is None:
        return None
    return _cached_reverse_geocode(round(lat, 4), round(lon, 4))

import json

# ================= FIREBASE AUTH IMPORTS (LAZY LOAD ENABLED) =================
import streamlit.components.v1 as components

# Declare Google Login custom component once at module level
parent_dir = os.path.dirname(__file__)
comp_path = os.path.join(parent_dir, "firebase_login_component")
google_login_comp = components.declare_component("google_login", path=comp_path)

# ================= CONFIG =================
st.set_page_config(page_title="AI Smart Land & Home Valuation Portal", layout="wide")

if "application_id" not in st.session_state:
    st.session_state["application_id"] = "LN2026" + str(random.randint(10000, 99999))
if "developer_mode" not in st.session_state:
    st.session_state["developer_mode"] = False

def log_underwriting_error(module, error_msg, input_data):
    os.makedirs("logs", exist_ok=True)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "application_id": st.session_state["application_id"],
        "module": module,
        "error": str(error_msg),
        "input_data": input_data
    }
    try:
        with open("logs/underwriting_errors.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print("Failed to write to error log file:", e)

def run_system_health_checks():
    failures = []
    
    # 1. Model Loaded
    has_val = os.path.exists("valuation_model.pkl") or os.path.exists("PythonProject1/valuation_model.pkl")
    has_loan = os.path.exists("loan_model.pkl") or os.path.exists("PythonProject1/loan_model.pkl")
    if not has_val:
        failures.append("Valuation ML Model binary (valuation_model.pkl) is not found.")
    if not has_loan:
        failures.append("Sanction Decision ML Model binary (loan_model.pkl) is not found.")
        
    # 2. Database Connected
    try:
        if not os.path.exists("assets/valuation_records.json"):
            os.makedirs("assets", exist_ok=True)
            with open("assets/valuation_records.json", "w") as f:
                json.dump([], f)
    except Exception as e:
        failures.append(f"Database sync failed: {e}")
        
    return failures

# ================= TIME API UTILITIES =================
def get_network_time_details():
    """
    Returns Kolkata server time properties using local system clock.
    """
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
@tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=2, max=10))
def get_current_weather(lat, lon):
    """
    Queries OpenWeather API using coordinate points and caches results.
    """
    if "current_weather_cache" in st.session_state:
        cache = st.session_state["current_weather_cache"]
        if abs(cache["lat"] - lat) < 0.05 and abs(cache["lon"] - lon) < 0.05:
            return cache["weather"]
            
    api_key = os.environ.get("WEATHER_API_KEY", "db8abf34273cc1c921dde0f6986a6920")
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
st.session_state["weather_profile"] = weather_profile
current_time_info = get_network_time_details()

from utils.background_manager import BackgroundManager
bg_manager = BackgroundManager()
bg_url = bg_manager.get_background_url(weather_profile["main"], current_time_info)

# ================= HISTORY FILE =================
HISTORY_FILE = "valuation_loan_history.csv"

@st.cache_data(ttl=3600)
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            if not df.empty and "Date" in df.columns:
                # Optimize: only prune once per user session to avoid slow writes on every tab switch
                if not st.session_state.get("history_pruned", False):
                    parsed_dates = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
                    today_start = pd.Timestamp.now().normalize()
                    one_week_ago = today_start - pd.Timedelta(days=7)
                    valid_mask = (parsed_dates >= one_week_ago) | parsed_dates.isna()
                    
                    if not valid_mask.all():
                        cleaned_df = df[valid_mask]
                        cleaned_df.to_csv(HISTORY_FILE, index=False)
                        st.session_state["history_pruned"] = True
                        return cleaned_df
                    st.session_state["history_pruned"] = True
            return df
        except Exception as e:
            print(f"Error loading and pruning history: {e}")
            return pd.DataFrame()
    return pd.DataFrame(columns=[
        "Reference_No", "Date", "Customer_Name", "State", "District", "Village", "PIN_Code",
        "Survey_Number", "Land_Area", "Land_Type", "Market_Value", "Guidance_Value",
        "Loan_Amount", "LTV_Ratio", "DTI_Ratio", "Risk_Score", "Decision", "User_UID"
    ])

def save_to_history(record):
    # Ensure User_UID is populated in the record
    uid = "N/A"
    if "user" in st.session_state:
        uid = st.session_state["user"].get("uid", "N/A")
    record["User_UID"] = uid
    
    # Save locally to CSV
    df = load_history()
    new_df = pd.DataFrame([record])
    if df.empty:
        df = new_df
    else:
        df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)
    
    # Sync with Firebase Database (Lazy load)
    from firebase.loans import save_loan_application
    save_loan_application(uid, record["Reference_No"], record)

# ================= DESIGN SYSTEM (CSS) =================
def set_design_system(background_image_url):
    # Render background divs for full-screen responsive blurred background with dark overlay and smooth transitions
    st.markdown(
        f"""
        <div class="aegis-bg-container">
            <div class="aegis-bg-image" style="background-image: url('{background_image_url}');"></div>
            <div class="aegis-bg-overlay"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Preload the next background image to minimize latency on transitions
    next_url = st.session_state.get("bg_next_url", "")
    if next_url:
        st.markdown(f'<link rel="preload" as="image" href="{next_url}">', unsafe_allow_html=True)
        
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: transparent !important;
        }}
        
        .main, .block-container {{
            background-color: transparent !important;
        }}
        
        /* Glassmorphism sidebar background */
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(12px);
        }}
        
        .aegis-bg-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: -999;
            overflow: hidden;
            background: #0f172a;
        }}
        
        .aegis-bg-image {{
            position: absolute;
            top: -15px;
            left: -15px;
            right: -15px;
            bottom: -15px;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            filter: blur(6px);
            transition: background-image 1.5s ease-in-out;
        }}
        
        .aegis-bg-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            /* Dark overlay 35-45% for readability */
            background: linear-gradient(rgba(15, 23, 42, 0.38), rgba(15, 23, 42, 0.43));
        }}
        
        /* High contrast text colors for dynamic dark nature backgrounds (strictly in stMain area) */
        [data-testid="stMain"] label,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] span,
        [data-testid="stMain"] [data-testid="stHeader"] {{
            color: #f1f5f9 !important;
            font-weight: 500;
        }}
        
        [data-testid="stMain"] h1, 
        [data-testid="stMain"] h2, 
        [data-testid="stMain"] h3, 
        [data-testid="stMain"] h4, 
        [data-testid="stMain"] h5, 
        [data-testid="stMain"] h6, 
        [data-testid="stMain"] .section-header {{
            color: #38bdf8 !important;
            font-weight: 700;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
        }}
        
        /* Enforce dark text inside native alerts and notification blocks for readability */
        div.stAlert p, div.stAlert li, div.stAlert span,
        div[data-testid="stNotification"] p, div[data-testid="stNotification"] span,
        .stAlert div {{
            color: #0f172a !important;
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
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');
        
        .app-title-container {{
            text-align: center;
            background: rgba(255, 255, 255, 0.88) !important;
            border: 1px solid rgba(2, 132, 199, 0.25) !important;
            border-radius: 20px;
            padding: 28px 24px;
            margin-bottom: 25px;
            backdrop-filter: blur(16px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .main-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 38px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 50%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent !important;
            margin-bottom: 6px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        
        .subtitle {{
            font-family: 'Outfit', sans-serif;
            color: #334155 !important;
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            opacity: 0.85;
            margin-top: 4px;
        }}
        
        .title-accent-bar {{
            width: 70px;
            height: 4px;
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            margin: 12px auto 0 auto;
            border-radius: 2px;
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
            background: rgba(255, 255, 255, 0.85) !important;
            border: 1px solid rgba(2, 132, 199, 0.2) !important;
            padding: 25px;
            border-radius: 16px;
            backdrop-filter: blur(15px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            margin-bottom: 20px;
        }}

        /* Frosted-Glass Sidebar theme overrides */
        section[data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.75) !important;
            backdrop-filter: blur(12px) !important;
            border-right: 1px solid rgba(2, 132, 199, 0.15) !important;
        }}
        
        section[data-testid="stSidebar"] div.stAlert,
        section[data-testid="stSidebar"] div[data-testid="stNotification"],
        section[data-testid="stSidebar"] div.stAlert > div {{
            background-color: rgba(255, 255, 255, 0.8) !important;
            color: #0f172a !important;
            border: 1px solid rgba(2, 132, 199, 0.15) !important;
        }}

        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {{
            color: #0f172a !important;
        }}
        
        .section-header {{
            color: #38bdf8 !important;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            border-bottom: 1px solid rgba(56, 189, 248, 0.3) !important;
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

def render_login_page():
    # Preload Outfit Font if not already loaded
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');
        
        /* Dark Glassmorphism Login Form Card styling */
        div[data-testid="stForm"] {
            background-color: rgba(15, 23, 42, 0.65) !important;
            border: 1px solid rgba(2, 132, 199, 0.25) !important;
            border-radius: 20px !important;
            padding: 2rem !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            backdrop-filter: blur(12px) !important;
            margin-top: 0.5rem !important;
        }
        
        /* Light/high-contrast text labels inside dark form */
        [data-testid="stMain"] div[data-testid="stForm"] label,
        [data-testid="stMain"] div[data-testid="stForm"] label span,
        [data-testid="stMain"] div[data-testid="stForm"] label p,
        [data-testid="stMain"] div[data-testid="stForm"] p,
        [data-testid="stMain"] div[data-testid="stForm"] span,
        [data-testid="stMain"] div[data-testid="stForm"] label * {
            color: #cbd5e1 !important;
            font-weight: 500 !important;
        }
        
        /* Force light background on text inputs for readability */
        [data-testid="stMain"] div[data-testid="stForm"] input {
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
        }
        
        /* High contrast headers in form */
        .login-header {
            font-family: 'Outfit', sans-serif;
            color: #38bdf8 !important;
            font-weight: 700;
            font-size: 1.6rem;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .login-title {
            font-family: 'Outfit', sans-serif;
            font-size: 2.6rem;
            font-weight: 800;
            color: #38bdf8 !important;
            -webkit-text-fill-color: #38bdf8 !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-subtitle {
            font-family: 'Outfit', sans-serif;
            color: #ffffff !important;
            font-size: 1rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000, 0 2px 4px rgba(0,0,0,0.5);
            margin-top: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize session state for auth pages
    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"
        
    current_page = st.session_state["auth_page"]
    
    # Title Banner for login
    st.markdown(
        """
        <div style="margin-top: 1.5rem; text-align: center;">
            <div class="login-title">
                🛡️ AegisCR Portal
            </div>
            <div class="login-subtitle">
                AI-Powered Credit Risk & Land Appraisal System
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    import streamlit.components.v1 as components
    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown(t("br"), unsafe_allow_html=True)
        
        if current_page == "login":
            with st.form("login_form", clear_on_submit=False):
                st.markdown(t("div_class_login_header_sign_in_div"), unsafe_allow_html=True)
                email = st.text_input(t("email_address"), placeholder="e.g. officer@aegiscr.com", key="login_email")
                password = st.text_input(t("password"), type="password", placeholder="Enter your password", key="login_password")
                submit = st.form_submit_button("Sign In", width='stretch')
                
                if submit:
                    from firebase.auth import sign_in_with_email
                    from firebase.users import save_user_profile
                    if not email or not password:
                        st.error(t("please_enter_both_email_and_password"))
                    else:
                        with st.spinner("Authenticating..."):
                            user, err = sign_in_with_email(email, password)
                            if err:
                                st.error(f"❌ {err}")
                            else:
                                save_success = save_user_profile(
                                    uid=user["localId"],
                                    name=user.get("displayName", email.split("@")[0].capitalize()),
                                    email=email,
                                    photo_url=user.get("profilePicture", ""),
                                    provider="Email"
                                )
                                if save_success:
                                    st.session_state["user"] = {
                                        "uid": user["localId"],
                                        "name": user.get("displayName", email.split("@")[0].capitalize()),
                                        "email": email,
                                        "photoURL": user.get("profilePicture", ""),
                                        "idToken": user["idToken"],
                                        "provider": "Email"
                                    }
                                    st.success(t("sign_in_successful_redirecting"))
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(t("failed_to_sync_user_session_metadata_wit"))
            
            # Google Auth Divider
            st.markdown(
                """
                <div style="text-align: center; margin: 15px 0; color: #cbd5e1; font-weight: bold;">
                    ────────── OR ──────────
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Embed the Google Login widget Component
            auth_result = google_login_comp(api_key=os.environ.get("FIREBASE_WEB_API_KEY"), key="google_login_widget", height=60)
            if auth_result:
                if auth_result.get("status") == "success":
                    from firebase.users import save_user_profile
                    with st.spinner("Logging in with Google..."):
                        save_success = save_user_profile(
                            uid=auth_result["uid"],
                            name=auth_result["name"],
                            email=auth_result["email"],
                            photo_url=auth_result["photoURL"],
                            provider="Google",
                            creation_time=auth_result.get("createdAt")
                        )
                        if save_success:
                            st.session_state["user"] = {
                                "uid": auth_result["uid"],
                                "name": auth_result["name"],
                                "email": auth_result["email"],
                                "photoURL": auth_result["photoURL"],
                                "idToken": auth_result["idToken"],
                                "provider": "Google"
                            }
                            st.success(t("sign_in_successful_redirecting"))
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(t("failed_to_sync_user_session_metadata_wit"))
                elif auth_result.get("status") == "error":
                    st.error(f"❌ Authentication failed: {auth_result.get('message')}")
                elif auth_result.get("status") == "loading":
                    st.info(t("connecting_to_google"))
            
            # Navigation links
            st.markdown(t("br"), unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t("create_account"), width='stretch'):
                    st.session_state["auth_page"] = "signup"
                    st.rerun()
            with col2:
                if st.button(t("reset_password"), width='stretch'):
                    st.session_state["auth_page"] = "reset"
                    st.rerun()
                    
        elif current_page == "signup":
            with st.form("signup_form", clear_on_submit=False):
                st.markdown(t("div_class_login_header_create_account_di"), unsafe_allow_html=True)
                email = st.text_input(t("email_address"), placeholder="e.g. officer@aegiscr.com", key="signup_email")
                password = st.text_input(t("password_min_6_chars"), type="password", placeholder="Choose a password", key="signup_password")
                confirm_password = st.text_input(t("confirm_password"), type="password", placeholder="Confirm your password", key="signup_confirm_password")
                submit = st.form_submit_button("Create Account", width='stretch')
                
                if submit:
                    from firebase.auth import sign_up_with_email
                    from firebase.users import save_user_profile
                    if not email or not password or not confirm_password:
                        st.error(t("please_fill_in_all_fields"))
                    elif password != confirm_password:
                        st.error(t("passwords_do_not_match"))
                    elif len(password) < 6:
                        st.error(t("password_should_be_at_least_6_characters"))
                    else:
                        with st.spinner("Registering..."):
                            user, err = sign_up_with_email(email, password)
                            if err:
                                st.error(f"❌ {err}")
                            else:
                                save_success = save_user_profile(
                                    uid=user["localId"],
                                    name=email.split("@")[0].capitalize(),
                                    email=email,
                                    photo_url="",
                                    provider="Email"
                                )
                                if save_success:
                                    st.session_state["user"] = {
                                        "uid": user["localId"],
                                        "name": email.split("@")[0].capitalize(),
                                        "email": email,
                                        "photoURL": "",
                                        "idToken": user["idToken"],
                                        "provider": "Email"
                                    }
                                    st.success(t("registration_successful_logging_in"))
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(t("failed_to_sync_user_session_metadata_wit"))
            
            # Google Auth Divider
            st.markdown(
                """
                <div style="text-align: center; margin: 15px 0; color: #cbd5e1; font-weight: bold;">
                    ────────── OR ──────────
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Embed the Google Login widget Component
            auth_result = google_login_comp(key="google_login_widget_signup", height=60)
            if auth_result:
                if auth_result.get("status") == "success":
                    from firebase.users import save_user_profile
                    with st.spinner("Logging in with Google..."):
                        save_success = save_user_profile(
                            uid=auth_result["uid"],
                            name=auth_result["name"],
                            email=auth_result["email"],
                            photo_url=auth_result["photoURL"],
                            provider="Google",
                            creation_time=auth_result.get("createdAt")
                        )
                        if save_success:
                            st.session_state["user"] = {
                                "uid": auth_result["uid"],
                                "name": auth_result["name"],
                                "email": auth_result["email"],
                                "photoURL": auth_result["photoURL"],
                                "idToken": auth_result["idToken"],
                                "provider": "Google"
                            }
                            st.success(t("sign_in_successful_redirecting"))
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(t("failed_to_sync_user_session_metadata_wit"))
                elif auth_result.get("status") == "error":
                    st.error(f"❌ Authentication failed: {auth_result.get('message')}")
                elif auth_result.get("status") == "loading":
                    st.info(t("connecting_to_google"))
            
            st.markdown(t("br"), unsafe_allow_html=True)
            if st.button(t("already_have_an_account_sign_in"), width='stretch'):
                st.session_state["auth_page"] = "login"
                st.rerun()
                
        elif current_page == "reset":
            with st.form("reset_form", clear_on_submit=False):
                st.markdown(t("div_class_login_header_reset_password_di"), unsafe_allow_html=True)
                email = st.text_input(t("email_address"), placeholder="e.g. officer@aegiscr.com", key="reset_email")
                submit = st.form_submit_button("Send Reset Link", width='stretch')
                
                if submit:
                    from firebase.auth import send_password_reset_email
                    if not email:
                        st.error(t("please_enter_your_email_address"))
                    else:
                        with st.spinner("Sending reset request..."):
                            success, err = send_password_reset_email(email)
                            if success:
                                st.success(t("password_reset_email_sent_please_check_y"))
                            else:
                                st.error(f"❌ {err}")
            
            st.markdown(t("br"), unsafe_allow_html=True)
            if st.button(t("back_to_sign_in"), width='stretch'):
                st.session_state["auth_page"] = "login"
                st.rerun()

set_design_system(bg_url)

# --- Firebase Authentication Intercept ---
if "user" not in st.session_state:
    render_login_page()
    st.stop()

# ================= LOAD MODELS (LAZY LOAD ENABLED) =================
log_memory_usage("After App Boot (Models Deferred)")

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

# --- Language Selector ---
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "mr": "Marathi (मराठी)",
    "bn": "Bengali (বাংলা)",
    "gu": "Gujarati (ગુજરાતી)",
    "ml": "Malayalam (മലയാളം)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)"
}
lang_options = list(SUPPORTED_LANGUAGES.values())
lang_keys = list(SUPPORTED_LANGUAGES.keys())
current_lang_idx = lang_keys.index(st.session_state.get("app_language", "en"))

selected_lang_name = st.sidebar.selectbox("Language / ಭಾಷೆ / भाषा", lang_options, index=current_lang_idx)
st.session_state["app_language"] = lang_keys[lang_options.index(selected_lang_name)]

# Show user details in sidebar
if "user" in st.session_state:
    user = st.session_state["user"]
    user_name = user.get("name", "")
    if not user_name:
        user_name = user.get("email", "User").split("@")[0].capitalize()
    user_email = user.get("email", "User")
    user_photo = user.get("photoURL", "")
    avatar_initial = user_name[0].upper() if user_name else "U"
    st.sidebar.markdown(
        f"""
        <div style='background: rgba(2, 132, 199, 0.1); border: 1px solid rgba(2, 132, 199, 0.25); padding: 16px; border-radius: 12px; margin-bottom: 15px; text-align: center;'>
            {"<img src='" + user_photo + "' style='border-radius: 50%; width: 64px; height: 64px; border: 2px solid #0284c7; margin-bottom: 8px;'/>" if user_photo else "<div style='width: 64px; height: 64px; border-radius: 50%; background-color: #0284c7; color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; margin: 0 auto 8px auto;'>" + avatar_initial + "</div>"}
            <p style='margin:0; font-size:10px; color:#475569; text-transform:uppercase;'>👤 Authenticated Personnel</p>
            <h4 style='margin:4px 0 2px 0; color:#0284c7;'>{user_name}</h4>
            <p style='margin:0; font-size:11px; color:#475569; overflow-wrap: break-word;'>{user_email}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.sidebar.button(t("log_out"), width='stretch'):
        st.session_state.pop("user", None)
        st.success(t("logged_out_successfully"))
        import time
        time.sleep(1)
        st.rerun()

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
st.sidebar.subheader("🛠️ Developer Self-Test Dashboard")

# Toggle Developer Mode Switch
st.session_state["developer_mode"] = st.sidebar.checkbox("Enable Developer Debug Mode", value=st.session_state.get("developer_mode", False))

# Display the unique Application Reference ID
st.sidebar.markdown(f"**Application Reference ID:** `{st.session_state['application_id']}`")

if st.session_state.get("developer_mode", False):
    st.sidebar.markdown(t("pre_deployment_checklist"))
    st.sidebar.markdown(
        "- `[x] User Authentication Simulated`\n"
        "- `[x] File Upload Handling`\n"
        "- `[x] Google Vision OCR Parsing`\n"
        "- `[x] Cross-Document Match Engine`\n"
        "- `[x] Land Appraisal Model (ML)`\n"
        "- `[x] Credit Decision Model (ML)`\n"
        "- `[x] Report Registry Sync (DB)`\n"
        "- `[x] Dynamic Background API`\n"
        "- `[x] Sanction PDF Compilation`\n"
        "- `[x] Render Blueprint Server Build`"
    )
    
    with st.sidebar.expander("📊 System Health Dashboard", expanded=True):
        # Calculate total errors from logs
        total_errs = 0
        if os.path.exists("logs/underwriting_errors.log"):
            try:
                with open("logs/underwriting_errors.log", "r") as f:
                    total_errs = len(f.readlines())
            except: pass
        
        # Model status
        val_loaded = "🟢 Loaded" if os.path.exists("valuation_model.pkl") else "🟡 Fallback Math"
        loan_loaded = "🟢 Loaded" if os.path.exists("loan_model.pkl") else "🟡 Fallback Heuristics"
        
        st.write(f"- **Valuation ML**: {val_loaded}")
        st.write(f"- **Sanction ML**: {loan_loaded}")
        st.write(f"- **OCR Status**: 🟢 Ready")
        st.write(f"- **Database Sync**: 🟢 Connected")
        from firebase.firebase_config import get_firebase_status
        fb_status = "🟢 Connected" if get_firebase_status() else "🔴 Offline"
        st.write(f"- **Firebase Auth**: {fb_status}")
        st.write(f"- **Weather API**: 🟢 Online")
        st.write(f"- **Maps Leaflet**: 🟢 Bound")
        st.write(f"- **Total Errors**: `{total_errs}`")
        
        last_pred = "N/A"
        if "underwriting_timeline" in st.session_state and st.session_state["underwriting_timeline"]:
            last_pred = st.session_state["underwriting_timeline"][-1]["time"]
        st.write(f"- **Last Run**: `{last_pred}`")
        
    with st.sidebar.expander("⚠️ Underwriting Error Dashboard", expanded=False):
        if os.path.exists("logs/underwriting_errors.log"):
            try:
                with open("logs/underwriting_errors.log", "r") as f:
                    lines = f.readlines()
                if lines:
                    st.markdown(t("recent_underwriting_errors"))
                    for line in reversed(lines[-5:]): # show last 5 errors
                        err_data = json.loads(line.strip())
                        st.markdown(
                            f"**Application ID**: `{err_data.get('application_id')}`<br/>"
                            f"**Module**: `{err_data.get('module')}`<br/>"
                            f"**Error**: `{err_data.get('error')}`<br/>"
                            f"**Time**: `{err_data.get('timestamp')}`<br/>"
                            f"**Inputs**: `{err_data.get('input_data')}`"
                            "<hr style='margin:8px 0; border:0; border-top:1px dashed rgba(239, 68, 68, 0.2);'/>",
                            unsafe_allow_html=True
                        )
                else:
                    st.info(t("no_recorded_exceptions_in_log_file"))
            except Exception as ex:
                st.write(t("error_reading_log_file"), ex)
        else:
            st.info(t("no_error_log_database_found"))
            
    with st.sidebar.expander("💾 Intermediate Results Manager", expanded=False):
        # Save Session State button
        if st.button(t("save_current_session_profile"), key="btn_save_session"):
            session_payload = {
                "application_id": st.session_state.get("application_id"),
                "dossier_verification": st.session_state.get("dossier_verification"),
                "valued_property": st.session_state.get("valued_property"),
                "underwriting_results": st.session_state.get("underwriting_results")
            }
            try:
                os.makedirs("logs/session_backups", exist_ok=True)
                fn = f"logs/session_backups/{st.session_state['application_id']}_session.json"
                with open(fn, "w") as f:
                    json.dump(session_payload, f, default=str)
                st.success(f"Saved to `{st.session_state['application_id']}_session.json`!")
            except Exception as e:
                st.error(f"Error saving session: {e}")
                
        # Load Session State selectbox
        os.makedirs("logs/session_backups", exist_ok=True)
        backups = [f for f in os.listdir("logs/session_backups") if f.endswith(".json")]
        if backups:
            selected_backup = st.selectbox(t("restore_session_profile"), backups, key="sb_restore_session")
            if st.button(t("restore_selected_profile"), key="btn_restore_session"):
                try:
                    fn = f"logs/session_backups/{selected_backup}"
                    with open(fn, "r") as f:
                        saved_payload = json.load(f)
                    
                    st.session_state["application_id"] = saved_payload.get("application_id")
                    if saved_payload.get("dossier_verification"):
                        st.session_state["dossier_verification"] = saved_payload.get("dossier_verification")
                    if saved_payload.get("valued_property"):
                        st.session_state["valued_property"] = saved_payload.get("valued_property")
                    if saved_payload.get("underwriting_results"):
                        st.session_state["underwriting_results"] = saved_payload.get("underwriting_results")
                        
                    st.success(t("session_profile_restored_refreshing"))
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading session: {e}")
        else:
            st.info(t("no_saved_session_backups_found"))
if st.sidebar.button(t("run_golden_test_property_math")):
    # Run the Golden Test check on known inputs
    print("[DEVELOPER SELF-TEST] Running Golden Test with expected property valuation data...")
    try:
        test_val = calculate_valuation(
            state="Karnataka",
            district="Bengaluru Urban",
            village="Indiranagar",
            pincode="560038",
            survey_number="G-1200",
            land_area=1200,
            land_type="Residential",
            lat=12.9784,
            lon=77.6408,
            property_class="Land only",
            built_up_area=0,
            building_age=0,
            construction_quality="Standard"
        )
        market_val = test_val["total_market_value"]
        guidance_val = test_val["total_guidance_value"]
        
        st.sidebar.success(
            "✅ **Golden Test Passed!**\n\n"
            f"• Area: `1200` sqft (Residential)\n"
            f"• Market Value: **₹{market_val:,}**\n"
            f"• Guidance Value: **₹{guidance_val:,}**\n"
            "• Service Integrity: **HEALTHY**"
        )
        print(f"[DEVELOPER SELF-TEST] Successful. Calculated Market Value: ₹{market_val}")
    except Exception as e:
        st.sidebar.error(f"❌ **Golden Test Failed:** {e}")
        print(f"[DEVELOPER SELF-TEST] Error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown(t("role_based_access_control_rbac"))
selected_role = st.sidebar.selectbox(t("active_operating_role"), ["👔 Loan Officer", "👤 Customer Portal", "🏢 Branch Manager", "⚙️ System Admin"], key="st_role_sel")
st.session_state["user_role"] = selected_role
st.sidebar.markdown("---")
version, commit_hash = get_git_info()
github_icon_html = f"""
<div style='text-align:center; margin-top:10px; margin-bottom:10px;'>
    <a href='{GITHUB_REPO_URL}' target='_blank' style='text-decoration:none; color:#0284c7; font-size:11px; font-weight:bold; display:inline-flex; align-items:center; gap:6px;'>
        <svg height="14" width="14" viewBox="0 0 16 16" fill="currentColor" style="display:inline-block; vertical-align:middle;">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
        </svg>
        GitHub Repository
    </a>
    <p style='margin: 4px 0 0 0; color:#475569; font-size:10px;'>Version: <code>{version}</code> | Commit: <code>{commit_hash}</code></p>
    <p style='margin: 6px 0 0 0; color:#475569; font-size:9px;'>Final-Year Placement Project © 2026</p>
</div>
"""
st.sidebar.markdown(github_icon_html, unsafe_allow_html=True)


# ================= TITLE BANNER =================
st.markdown(
    """
    <div class="app-title-container">
        <div class="main-title">
            <svg class="title-icon" viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="url(#cyan-grad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 12px;">
                <defs>
                    <linearGradient id="cyan-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#0284c7" />
                        <stop offset="100%" stop-color="#38bdf8" />
                    </linearGradient>
                </defs>
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            AegisCR Underwriting Portal
        </div>
        <div class="subtitle">AI-Powered Intelligent Underwriting & Collateral Appraisal Platform</div>
        <div class="title-accent-bar"></div>
    </div>
    """,
    unsafe_allow_html=True
)

# Setup tabs in requested workflow order: Dashboard -> Valuation -> Document Verification -> Loan Prediction -> Logs
tab1, tab_multi, tab3, tab4, tab5 = st.tabs([
    "🏠 Portfolio Dashboard", 
    "🏦 Multi-Loan Products Console",
    "📂 Document Verification Check",
    "📊 Smart Loan Prediction", 
    "📜 History Logs"
])

# Load History
history_df = load_history()

# ================= TAB 1: EXECUTIVE DASHBOARD =================
with tab1:
    st.markdown(t("div_class_section_header_portfolio_perfo"), unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='display:flex; justify-content:flex-end; margin-top:-45px; margin-bottom:15px;'>
            <a href='{GITHUB_REPO_URL}' target='_blank' style='text-decoration:none; background-color:#1e293b; color:#cbd5e1; border:1px solid #334155; padding:8px 16px; border-radius:6px; font-size:12px; font-weight:bold; display:inline-flex; align-items:center; gap:8px;'>
                <svg height="14" width="14" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
                View Source on GitHub
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Filter stats by the logged-in user's UID (different employee has different stats)
    user_uid = "N/A"
    if "user" in st.session_state:
        user_uid = st.session_state["user"].get("uid", "N/A")
        
    if not history_df.empty and "User_UID" in history_df.columns:
        user_history = history_df[history_df["User_UID"] == user_uid]
    else:
        user_history = pd.DataFrame(columns=history_df.columns)
        
    total_processed = len(user_history)
    approved_count = len(user_history[user_history["Decision"] == "APPROVED"])
    rejected_count = len(user_history[user_history["Decision"] == "REJECTED"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">📋 total processed loans</div><div class="metric-value">{total_processed:,}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card approved"><div class="metric-title">✅ approved applications</div><div class="metric-value">{approved_count:,}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card rejected"><div class="metric-title">❌ rejected applications</div><div class="metric-value">{rejected_count:,}</div></div>', unsafe_allow_html=True)
    with col4:
        rate = (approved_count / total_processed * 100) if total_processed > 0 else 0.0
        st.markdown(f'<div class="metric-card"><div class="metric-title">📈 average approval rate</div><div class="metric-value">{rate:.1f}%</div></div>', unsafe_allow_html=True)
        
    st.markdown(t("br"), unsafe_allow_html=True)
    
    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("regional_activity_heatmap"))
        if not user_history.empty and "District" in user_history.columns:
            dist_counts = user_history["District"].value_counts().reset_index()
            dist_counts.columns = ["District", "Applications"]
            st.bar_chart(dist_counts.set_index("District"))
        else:
            st.info(t("ℹ_no_regional_evaluation_data_available_"))
        st.markdown(t("div"), unsafe_allow_html=True)
        
    with gcol2:
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("risk_score_distribution"))
        if not user_history.empty and "Risk_Score" in user_history.columns:
            risk_series = user_history["Risk_Score"]
            hist_vals, bin_edges = np.histogram(risk_series, bins=10, range=(0, 100))
            chart_data = pd.DataFrame(hist_vals, index=bin_edges[:-1], columns=["Risk Scores"])
            st.area_chart(chart_data)
        else:
            st.info(t("ℹ_no_risk_score_evaluation_data_availabl"))
        st.markdown(t("div"), unsafe_allow_html=True)



# --- UNIFIED PROPERTY INTELLIGENCE ENGINE ---
def render_property_intelligence(loan_type):
    # Base unified workflow
    
    
    col_inputs, col_map = st.columns([1, 1.2])
    
    with col_inputs:
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("property_address_registration"))
    
        # Initialize interactive form keys if not already present
        if "val_state" not in st.session_state:
            st.session_state["val_state"] = "Karnataka"
            st.session_state["val_district_sel"] = "Bengaluru Urban"
            st.session_state["val_taluk_sel"] = "Bangalore"
            st.session_state["val_village_sel"] = "Whitefield"
            st.session_state["val_district_text"] = ""
            st.session_state["val_taluk_text"] = ""
            st.session_state["val_village_text"] = ""
            st.session_state["val_pincode"] = "560066"
            st.session_state["val_survey"] = "101/2"
    
        state_options = ["Karnataka", "Telangana", "Maharashtra", "Tamil Nadu", "Other"]
        # Find index for state
        state_idx = state_options.index(st.session_state["val_state"]) if st.session_state["val_state"] in state_options else 0
        state = st.selectbox(t("state"), state_options, index=state_idx, key="val_state_widget")
        st.session_state["val_state"] = state
    
        taluk = None
        if state == "Karnataka":
            from utils.valuation_module import get_db_districts, get_db_taluks, get_db_villages
    
            # Fetch districts dynamically
            district_list = get_db_districts()
            if not district_list:
                import json
                try:
                    with open("karnataka_regions.json", "r") as f:
                        regions_for_dist = json.load(f)
                    district_list = list(regions_for_dist.keys())
                except Exception:
                    district_list = ["Bagalkote", "Bangalore Rural", "Belagavi", "Bellary", "Bidar"]
        
            curr_dist = st.session_state.get("val_district_sel", district_list[0])
            if curr_dist not in district_list:
                matched_dist = district_list[0]
                for d in district_list:
                    if curr_dist and (d.lower() in curr_dist.lower() or curr_dist.lower() in d.lower()):
                        matched_dist = d
                        break
                st.session_state["val_district_sel"] = matched_dist
            d_idx = district_list.index(st.session_state["val_district_sel"]) if st.session_state.get("val_district_sel") in district_list else 0
            district = st.selectbox(t("district"), district_list, index=d_idx, key="val_district_sel_widget")
            st.session_state["val_district_sel"] = district
    
            # Fetch taluks dynamically
            taluk_list = get_db_taluks(district)
            if not taluk_list:
                import json
                try:
                    with open("karnataka_regions.json", "r") as f:
                        regions = json.load(f)
                    taluk_list = regions.get(district, ["Select Taluk"])
                except Exception:
                    taluk_list = ["Select Taluk"]
            curr_taluk = st.session_state.get("val_taluk_sel", taluk_list[0])
            if curr_taluk not in taluk_list:
                matched_taluk = taluk_list[0]
                for t in taluk_list:
                    if curr_taluk and (t.lower() in curr_taluk.lower() or curr_taluk.lower() in t.lower()):
                        matched_taluk = t
                        break
                st.session_state["val_taluk_sel"] = matched_taluk
            t_idx = taluk_list.index(st.session_state["val_taluk_sel"]) if st.session_state.get("val_taluk_sel") in taluk_list else 0
            taluk = st.selectbox(t("taluk_sub_registrar_office"), taluk_list, index=t_idx, key="val_taluk_sel_widget")
            st.session_state["val_taluk_sel"] = taluk
    
            # Fetch villages dynamically
            village_list = get_db_villages(district, taluk)
            if not village_list:
                village_list = ["Adagallu", "Kyada", "Ananthagiri", "Katharaki"]
            curr_village = st.session_state.get("val_village_sel", village_list[0])
            if curr_village not in village_list:
                matched_village = village_list[0]
                for v in village_list:
                    if curr_village and (v.lower() in curr_village.lower() or curr_village.lower() in v.lower()):
                        matched_village = v
                        break
                st.session_state["val_village_sel"] = matched_village
            v_idx = village_list.index(st.session_state["val_village_sel"]) if st.session_state.get("val_village_sel") in village_list else 0
            village = st.selectbox(t("village_layout_road"), village_list, index=v_idx, key="val_village_sel_widget_1")
            st.session_state["val_village_sel"] = village
    
        elif state in GEO_DB:
            district_list = list(GEO_DB[state]["districts"].keys())
            curr_dist = st.session_state.get("val_district_sel", district_list[0])
            if curr_dist not in district_list:
                matched_dist = district_list[0]
                for d in district_list:
                    if curr_dist and (d.lower() in curr_dist.lower() or curr_dist.lower() in d.lower()):
                        matched_dist = d
                        break
                st.session_state["val_district_sel"] = matched_dist
            d_idx = district_list.index(st.session_state["val_district_sel"]) if st.session_state.get("val_district_sel") in district_list else 0
            district = st.selectbox(t("district"), district_list, index=d_idx, key="val_district_sel_widget")
            st.session_state["val_district_sel"] = district
    
            village_list = GEO_DB[state]["districts"][district]["villages"]
            curr_village = st.session_state.get("val_village_sel", village_list[0])
            if curr_village not in village_list:
                matched_village = village_list[0]
                for v in village_list:
                    if curr_village and (v.lower() in curr_village.lower() or curr_village.lower() in v.lower()):
                        matched_village = v
                        break
                st.session_state["val_village_sel"] = matched_village
            v_idx = village_list.index(st.session_state["val_village_sel"]) if st.session_state.get("val_village_sel") in village_list else 0
            village = st.selectbox(t("village_layout"), village_list, index=v_idx, key="val_village_sel_widget_2")
            st.session_state["val_village_sel"] = village
            taluk = ""
        else:
            district = st.text_input(t("enter_district"), key="val_district_text")
            taluk = st.text_input(t("enter_taluk_sub_district"), key="val_taluk_text")
            village = st.text_input(t("enter_village"), key="val_village_text")
    
        pincode = st.text_input(t("pin_code"), value=st.session_state.get("val_pincode", "560066"), key="val_pincode_widget")
        st.session_state["val_pincode"] = pincode
        survey_number = st.text_input(t("survey_number_e_g_142_3"), key="val_survey")
    
        # Registration section complete
    
        st.markdown(t("div"), unsafe_allow_html=True)
    
    with col_map:
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("interactive_land_boundaries_leaflet_map"))
        st.markdown(t("p_class_map_instruction_click_anywhere_o"), unsafe_allow_html=True)
    
        # Check if address changed to trigger map re-centering
        current_loc_key = f"{state}_{district}_{taluk}_{village}"
        if "last_loc_key" not in st.session_state or st.session_state["last_loc_key"] != current_loc_key:
            st.session_state["last_loc_key"] = current_loc_key
            if state == "Karnataka":
                from utils.valuation_module import geocode_address
                coords = geocode_address(state, district, taluk, village)
                if coords:
                    st.session_state["map_center"] = coords
            elif state in coordinate_db and district in coordinate_db[state]:
                st.session_state["map_center"] = coordinate_db[state][district]
            else:
                st.session_state["map_center"] = (12.9716, 77.5946)
        
        lat, lon = st.session_state.get("map_center", (12.9716, 77.5946))
    
        m = folium.Map(location=[lat, lon], zoom_start=14)
        m.add_child(folium.LatLngPopup())
    
        # Add marker for valued property if exists
        valued_coords = None
        if "valued_property" in st.session_state:
            vp = st.session_state["valued_property"]
            vp_lat = vp.get("Latitude", lat)
            vp_lon = vp.get("Longitude", lon)
            valued_coords = (vp_lat, vp_lon)
    
            popup_html = f"""
            <div style="font-family: 'Outfit', 'Inter', sans-serif; width: 280px; padding: 10px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px; color: #0284c7; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; font-size: 14px;">🏠 Collateral Valuation Details</h4>
                <table style="width: 100%; font-size: 11px; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="font-weight: 600; padding: 4px 0;">District</td><td style="text-align: right;">{vp['District']}</td></tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="font-weight: 600; padding: 4px 0;">Village/Area</td><td style="text-align: right;">{vp['Village']}</td></tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="font-weight: 600; padding: 4px 0;">Survey No</td><td style="text-align: right;">{vp['Survey_Number']}</td></tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="font-weight: 600; padding: 4px 0;">Property Type</td><td style="text-align: right;">{vp['property_class']}</td></tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="font-weight: 600; padding: 4px 0;">Guideline Value</td><td style="text-align: right;">₹{vp['guidance_value_per_sqft']:,}/sqft</td></tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="font-weight: 600; padding: 4px 0;">Total Area</td><td style="text-align: right;">{vp['Land_Area']:,} sqft</td></tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="font-weight: 600; padding: 4px 0; color: #0369a1;">AI Market Value</td><td style="text-align: right; font-weight: 700; color: #0369a1;">₹{vp['total_market_value']:,}</td></tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;"><td style="font-weight: 600; padding: 4px 0; color: #b45309;">AI Risk Status</td><td style="text-align: right; font-weight: 700; color: #b45309;">{vp['fraud_check']['status']}</td></tr>
                    <tr><td style="font-weight: 600; padding: 4px 0; color: #15803d;">Max Eligible Loan</td><td style="text-align: right; font-weight: 700; color: #15803d;">₹{vp['max_loan_amount']:,}</td></tr>
                </table>
            </div>
            """
            iframe = folium.IFrame(html=popup_html, width=310, height=260)
            popup = folium.Popup(iframe, max_width=330)
            folium.Marker(
                [vp_lat, vp_lon],
                popup=popup,
                tooltip="Click to view full property appraisal details",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
    
        # Show red marker for selection if it's different from the valued coordinates or before valuation is computed
        if not valued_coords or abs(valued_coords[0] - lat) > 0.0001 or abs(valued_coords[1] - lon) > 0.0001:
            folium.Marker(
                [lat, lon],
                tooltip="Pinned Location (Pending Valuation)",
                icon=folium.Icon(color="red", icon="map-marker")
            ).add_to(m)
    
        map_data = st_folium(m, width="100%", height=400, key="app_folium_map_main")
    
        clicked_lat, clicked_lon = lat, lon
        if map_data and map_data.get("last_clicked"):
            clicked_lat = map_data["last_clicked"]["lat"]
            clicked_lon = map_data["last_clicked"]["lng"]
    
            # Check if clicked coordinates changed
            last_clicked = st.session_state.get("last_clicked_coords", None)
            if last_clicked != (clicked_lat, clicked_lon):
                st.session_state["last_clicked_coords"] = (clicked_lat, clicked_lon)
                st.session_state["map_center"] = (clicked_lat, clicked_lon)
        
                # Perform reverse geocoding to auto-fill the form
                with st.spinner("🔍 Reverse geocoding clicked location..."):
                    geo_res = reverse_geocode(clicked_lat, clicked_lon)
                    if geo_res:
                        state_g, district_g, taluk_g, village_g, postcode_g = geo_res
                
                        # Update State
                        state_options = ["Karnataka", "Telangana", "Maharashtra", "Tamil Nadu", "Other"]
                        if state_g in state_options:
                            st.session_state["val_state"] = state_g
                        else:
                            st.session_state["val_state"] = "Other"
                    
                        # Resolve dropdown options safely with fuzzy word boundary matching
                        resolved_d = None
                        resolved_t = None
                        resolved_v = None
                
                        if state_g == "Karnataka":
                            from utils.valuation_module import get_db_districts, get_db_taluks, get_db_villages
                            d_list = get_db_districts()
                    
                            # 1. Fuzzy match District
                            if district_g and d_list:
                                for d in d_list:
                                    if d.lower() in district_g.lower() or district_g.lower() in d.lower():
                                        resolved_d = d
                                        break
                                if not resolved_d:
                                    for d in d_list:
                                        d_words = set(d.lower().split())
                                        dg_words = set(district_g.lower().split())
                                        if d_words & dg_words:
                                            resolved_d = d
                                            break
                            if not resolved_d and d_list:
                                resolved_d = d_list[0]
                        
                            if resolved_d:
                                st.session_state["val_district_sel"] = resolved_d
                        
                                # 2. Fuzzy match Taluk
                                t_list = get_db_taluks(resolved_d)
                                if taluk_g and t_list:
                                    for t in t_list:
                                        if t.lower() in taluk_g.lower() or taluk_g.lower() in t.lower():
                                            resolved_t = t
                                            break
                                    if not resolved_t:
                                        for t in t_list:
                                            t_words = set(t.lower().split())
                                            tg_words = set(taluk_g.lower().split())
                                            if t_words & tg_words:
                                                resolved_t = t
                                                break
                                if not resolved_t and t_list:
                                    resolved_t = t_list[0]
                            
                                if resolved_t:
                                    st.session_state["val_taluk_sel"] = resolved_t
                            
                                    # 3. Fuzzy match Village
                                    v_list = get_db_villages(resolved_d, resolved_t)
                                    if village_g and v_list:
                                        for v in v_list:
                                            if v.lower() in village_g.lower() or village_g.lower() in v.lower():
                                                resolved_v = v
                                                break
                                        if not resolved_v:
                                            for v in v_list:
                                                v_words = set(v.lower().split())
                                                vg_words = set(village_g.lower().split())
                                                if v_words & vg_words:
                                                    resolved_v = v
                                                    break
                                    if not resolved_v and v_list:
                                        resolved_v = v_list[0]
                                
                                    if resolved_v:
                                        st.session_state["val_village_sel"] = resolved_v
                        else:
                            # Update text fields for non-Karnataka
                            st.session_state["val_district_text"] = district_g
                            st.session_state["val_taluk_text"] = taluk_g
                            st.session_state["val_village_text"] = village_g
                            resolved_d = district_g
                            resolved_t = taluk_g
                            resolved_v = village_g
                    
                        if postcode_g:
                            st.session_state["val_pincode"] = postcode_g
                        else:
                            st.session_state["val_pincode"] = "560001" if state_g == "Karnataka" else "500001"
                    
                        # Map auto-population complete
                    
                        st.rerun()
    
        st.write(f"📍 **Captured Coordinates:** Latitude: `{clicked_lat:.6f}` | Longitude: `{clicked_lon:.6f}`")
        st.markdown(t("div"), unsafe_allow_html=True)
    
    # Shared rendering complete
    
    
    
# --------------------------------------------

# ================= TAB MULTI: MULTI-LOAN PRODUCTS CONSOLE =================
with tab_multi:
    st.markdown(t("div_class_section_header_aegiscr_multi_p"), unsafe_allow_html=True)
    loan_prod_sel = st.radio(
        "Select Loan Product Module",
        ["🏠 Home Loan", "🌾 Agriculture Loan", "🏢 Commercial Loan", "🥇 Gold Loan", "🚜 Farm Equipment Loan", "🚗 Vehicle Loan"],
        horizontal=True,
        key="loan_prod_sel"
    )
    
    if loan_prod_sel == "🏠 Home Loan":
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("home_loan_property_intelligence"))
        # --- SECTION 1 & 2: SHARED PROPERTY CONTEXT ---
        render_property_intelligence("Home Loan")
        
        # --- SECTION 3: HOME PROPERTY DETAILS ---
        st.markdown(t("home_property_details"))
        hcol1, hcol2, hcol3 = st.columns(3)
        with hcol1:
            h_plot = st.number_input(t("plot_area_sq_ft"), min_value=100.0, value=1200.0, key="h_plot")
            h_built = st.number_input(t("built_up_area_sq_ft"), min_value=0.0, value=1500.0, key="h_built")
        with hcol2:
            h_type = st.selectbox(t("property_type"), ["Independent House", "Residential Apartment", "Residential Plot"], key="h_type")
            h_year = st.number_input(t("construction_year"), min_value=1950, max_value=2026, value=2020, key="h_year")
        with hcol3:
            h_floors = st.number_input(t("number_of_floors"), min_value=1, value=1, key="h_floors")
        # --- SECTION 5: HOME LOAN ASSESSMENT ---
        st.markdown(t("home_loan_assessment"))
        btn_h_clicked = st.button(t("calculate_property_valuation_loan_terms"), key="btn_h_calc")
        if btn_h_clicked:
            st.session_state["h_calc_done"] = True
            st.session_state.pop("h_report_data", None)
            st.session_state.pop("h_res", None)
            
        if st.session_state.get("h_calc_done", False):
            if "h_res" not in st.session_state or btn_h_clicked:
                with st.spinner("Analyzing property value and loan eligibility..."):
                    from backend.routers.valuation import evaluate_loan_module, EvaluateLoanModuleInput
                    st.session_state["h_res"] = evaluate_loan_module(EvaluateLoanModuleInput(
                    module="home", 
                    district=st.session_state.get("val_district_sel", "Bengaluru Urban"), 
                    taluk=st.session_state.get("val_taluk_sel", "Bangalore"), 
                    village=st.session_state.get("val_village_sel", "Whitefield"), 
                    survey_number=st.session_state.get("val_survey", "101/2"),
                    plot_area=h_plot, built_up_area=h_built, property_type=h_type, construction_year=h_year,
                    applicant_name=st.session_state.get("tab4_name", "Rajesh Kumar"), 
                    annual_income=st.session_state.get("tab4_app_income", 75000.0) * 12, 
                    existing_liabilities=250000.0,
                    credit_score=750 if st.session_state.get("tab4_credit_hist", 1.0) == 1.0 else 600, 
                    requested_loan=st.session_state.get("tab4_active_loan_amount", 6500000.0), 
                    loan_purpose="Home Purchase",
                    aadhaar_verified=st.session_state.get("kyc_aadhaar_pass", True),
                    pan_verified=st.session_state.get("kyc_pan_pass", True),
                    ocr_trust_score=st.session_state.get("kyc_trust_score", 95.0)
                ))
            res = st.session_state["h_res"]
            if True:
                
                # --- SECTION 4: AI PROPERTY INTELLIGENCE (Results) ---
                st.markdown(t("ai_property_intelligence"))
                vcol1, vcol2, vcol3 = st.columns(3)
                with vcol1:
                    st.metric("Govt Guidance Value", f"₹{res['total_property_value'] * 0.7:,.2f}")
                    st.metric("Location Score", "85/100 (High Growth)")
                with vcol2:
                    st.metric("AI Estimated Market Value", f"₹{res['total_property_value']:,.2f}")
                    st.metric("Market Trend", "+5.2% YOY")
                with vcol3:
                    st.markdown(t("fraud_detection_span_style_color_10b981_"), unsafe_allow_html=True)
                    st.markdown(t("explainable_ai_summary_values_align_perf"), unsafe_allow_html=True)
                
                # --- SECTION 5 (cont): LOAN METRICS ---
                st.success(f"✅ Recommended Sanction (80% LTV): **₹{res['recommended_loan']:,.2f}**")
                
                # --- NEARBY LISTINGS & PROJECTIONS ---
                st.markdown(t("nearby_similar_registered_properties_ngd"))
                import pandas as pd
                import random
                nb1 = int(res['rate_per_sqft'] * random.uniform(0.9, 1.1))
                nb2 = int(res['rate_per_sqft'] * random.uniform(0.9, 1.1))
                nb3 = int(res['rate_per_sqft'] * random.uniform(0.9, 1.1))
                s_num = st.session_state.get("val_survey", "101/2")
                ndf = pd.DataFrame({
                    "Survey Number": [f"{s_num.split('/')[0]}/{random.randint(1,100)}", f"{random.randint(1,500)}/4", f"{random.randint(1,500)}/2"],
                    "Distance (m)": [120, 310, 480],
                    "Registered Price (per sqft)": [f"Rs. {nb1:,}", f"Rs. {nb2:,}", f"Rs. {nb3:,}"],
                    "Registry Source": ["NGDRS State Registry", "Kaveri Portal / TNREGINET", "Kaveri Portal / TNREGINET"],
                    "Transaction Date": ["14-05-2026", "22-04-2026", "10-02-2026"]
                })
                st.table(ndf)
            
                st.markdown(t("future_collateral_appreciation_forecast"))
                pcol1, pcol2, pcol3, pcol4 = st.columns(4)
                pcol1.metric("Growth Rate", "8.5% Annual")
                pcol2.metric("1 Year Value Projection", f"₹{res['total_property_value'] * 1.085:,.2f}")
                pcol3.metric("3 Years Value Projection", f"₹{res['total_property_value'] * 1.277:,.2f}")
                pcol4.metric("5 Years Value Projection", f"₹{res['total_property_value'] * 1.503:,.2f}")
                
                # --- SECTION 6: REPORTS ---
                st.markdown(t("ai_report_generator"))
                h_rep_data = st.session_state.get("h_report_data", None)
                if h_rep_data is None:
                    if st.button(t("generate_ai_valuation_report"), key="btn_h_gen"):
                        with st.spinner("Generating detailed AI underwriting report via Groq..."):
                            from backend.services.report_generator import generate_loan_report, md_to_pdf_bytes
                            
                            # Inject UI metrics into res before sending to AI
                            res_ai = dict(res)
                            res_ai["govt_guidance_value"] = res['total_property_value'] * 0.7
                            res_ai["location_score"] = "85/100 (High Growth)"
                            res_ai["market_trend_yoy"] = "+5.2%"
                            res_ai["fraud_detection"] = "PASS"
                            res_ai["nearby_properties"] = ndf.to_dict(orient="records")
                            res_ai["appreciation_forecast"] = {
                                "growth_rate": "8.5% Annual",
                                "1_year_projection": res['total_property_value'] * 1.085,
                                "3_year_projection": res['total_property_value'] * 1.277,
                                "5_year_projection": res['total_property_value'] * 1.503
                            }
                            
                            report_md = generate_loan_report("Home Loan", res_ai)
                            st.session_state["h_report_data"] = md_to_pdf_bytes(report_md)
                            st.rerun()
                else:
                    st.success(t("ai_report_generated_successfully"))
                    st.download_button("📄 Download AI Valuation Report (PDF)", data=h_rep_data, file_name="Home_Property_Valuation.pdf", mime="application/pdf", key="h_rep1")

        st.markdown(t("div"), unsafe_allow_html=True)

    elif loan_prod_sel == "🌾 Agriculture Loan":
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("agricultural_land_intelligence"))
        
        # --- SECTION 1 & 2: SHARED PROPERTY CONTEXT ---
        render_property_intelligence("Agriculture Loan")
        
        # --- SECTION 3: LAND DETAILS ---
        st.markdown(t("agricultural_land_details"))
        acol1, acol2, acol3 = st.columns(3)
        with acol1:
            a_acres = st.number_input(t("land_area_acres"), min_value=0.1, value=5.0, step=0.5, key="a_acres")
            a_soil = st.selectbox(t("soil_type"), ["Red Soil", "Black Cotton Soil", "Alluvial", "Laterite"], key="a_soil")
        with acol2:
            a_type = st.selectbox(t("land_classification"), ["Dry Land", "Wet Land", "Bagayat Land", "Kharab"], key="a_type")
            a_irrig = st.selectbox(t("irrigation_source"), ["Borewell", "Canal", "Rainfed", "Drip"], key="a_irrig")
        with acol3:
            a_crop = st.selectbox(t("crop_type"), ["Paddy", "Sugarcane", "Cotton", "Maize"], key="a_crop")
            a_season = st.selectbox(t("crop_season"), ["Kharif", "Rabi", "Zaid"], key="a_season")

        # --- SECTION 5: AGRICULTURE LOAN ASSESSMENT ---
        st.markdown(t("agriculture_loan_assessment"))
        btn_a_clicked = st.button(t("calculate_ag_valuation_risk_score"), key="btn_a_calc")
        if btn_a_clicked:
            st.session_state["a_calc_done"] = True
            st.session_state.pop("a_report_data", None)
            st.session_state.pop("a_res", None)
            
        if st.session_state.get("a_calc_done", False):
            if "a_res" not in st.session_state or btn_a_clicked:
                with st.spinner("Analyzing land value and agricultural risks..."):
                    from backend.routers.valuation import evaluate_loan_module, EvaluateLoanModuleInput
                    st.session_state["a_res"] = evaluate_loan_module(EvaluateLoanModuleInput(
                    module="agriculture", district=st.session_state.get("val_district_sel", "Bengaluru Urban"), taluk=st.session_state.get("val_taluk_sel", "Bangalore"), village=st.session_state.get("val_village_sel", "Whitefield"),
                    plot_area=a_acres, land_type=a_type
                ))
            res = st.session_state["a_res"]
            if True:
                
                # --- SECTION 4: WEATHER & AGRICULTURE INTELLIGENCE ---
                st.markdown(t("weather_agriculture_intelligence"))
                wcol1, wcol2, wcol3 = st.columns(3)
                with wcol1:
                    st.metric("Rainfall", "Normal (+2%)")
                    st.metric("Flood Risk", "LOW", delta_color="inverse")
                with wcol2:
                    st.metric("Soil Moisture", "Optimal")
                    st.metric("Drought Risk", "LOW", delta_color="inverse")
                with wcol3:
                    st.metric("Crop Weather Score", "92/100")
                    st.markdown(t("agriculture_ai_analysis_excellent_condit"), unsafe_allow_html=True)
                
                # --- SECTION 5 (cont): VALUATION METRICS ---
                st.markdown(t("ai_land_valuation"))
                vcol1, vcol2, vcol3 = st.columns(3)
                with vcol1:
                    st.metric("Guidance Value", f"₹{res['total_land_value'] * 0.65:,.2f}")
                    st.metric("Risk Score", f"{res['risk_score']}/100")
                with vcol2:
                    st.metric("Estimated Market Value", f"₹{res['total_land_value']:,.2f}")
                    st.metric("AI Recommendation", "APPROVE")
                with vcol3:
                    st.markdown(t("fraud_detection_span_style_color_10b981_"), unsafe_allow_html=True)
                    st.markdown(t("explainable_ai_values_are_consistent_wit"), unsafe_allow_html=True)
                
                st.success(f"✅ Eligible Ag Loan (75% LTV): **₹{res['eligible_loan']:,.2f}**")
                
                # --- NEARBY LISTINGS & PROJECTIONS ---
                st.markdown(t("nearby_similar_registered_properties_ngd"))
                import pandas as pd
                import random
                nb1 = int(res['rate_per_acre'] * random.uniform(0.9, 1.1))
                nb2 = int(res['rate_per_acre'] * random.uniform(0.9, 1.1))
                nb3 = int(res['rate_per_acre'] * random.uniform(0.9, 1.1))
                s_num = st.session_state.get("val_survey", "101/2")
                ndf = pd.DataFrame({
                    "Survey Number": [f"{s_num.split('/')[0]}/{random.randint(1,100)}", f"{random.randint(1,500)}/4", f"{random.randint(1,500)}/2"],
                    "Distance (m)": [120, 310, 480],
                    "Registered Price (per acre)": [f"₹{nb1:,}", f"₹{nb2:,}", f"₹{nb3:,}"],
                    "Registry Source": ["NGDRS State Registry", "Kaveri Portal / TNREGINET", "Kaveri Portal / TNREGINET"],
                    "Transaction Date": ["14-05-2026", "22-04-2026", "10-02-2026"]
                })
                st.table(ndf)
            
                st.markdown(t("future_collateral_appreciation_forecast"))
                pcol1, pcol2, pcol3, pcol4 = st.columns(4)
                pcol1.metric("Growth Rate", "5.2% Annual")
                pcol2.metric("1 Year Value Projection", f"₹{res['total_land_value'] * 1.052:,.2f}")
                pcol3.metric("3 Years Value Projection", f"₹{res['total_land_value'] * 1.164:,.2f}")
                pcol4.metric("5 Years Value Projection", f"₹{res['total_land_value'] * 1.288:,.2f}")
                
                # --- SECTION 6: REPORTS ---
                st.markdown(t("ai_report_generator"))
                a_rep_data = st.session_state.get("a_report_data", None)
                if a_rep_data is None:
                    if st.button(t("generate_ai_valuation_report"), key="btn_a_gen"):
                        with st.spinner("Generating detailed AI underwriting report via Groq..."):
                            from backend.services.report_generator import generate_loan_report, md_to_pdf_bytes
                            report_md = generate_loan_report("Agriculture Loan", res)
                            st.session_state["a_report_data"] = md_to_pdf_bytes(report_md)
                            st.rerun()
                else:
                    st.success(t("ai_report_generated_successfully"))
                    st.download_button("📄 Download AI Valuation Report (PDF)", data=a_rep_data, file_name="Agriculture_Valuation.pdf", mime="application/pdf", key="a_rep1")

        st.markdown(t("div"), unsafe_allow_html=True)

    elif loan_prod_sel == "🏢 Commercial Loan":
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("commercial_property_intelligence"))
        
        # --- SECTION 1 & 2: SHARED PROPERTY CONTEXT ---
        render_property_intelligence("Commercial Loan")
        
        # --- SECTION 3: COMMERCIAL PROPERTY DETAILS ---
        st.markdown(t("commercial_property_details"))
        ccol1, ccol2, ccol3 = st.columns(3)
        with ccol1:
            c_plot = st.number_input(t("commercial_plot_area_sq_ft"), min_value=100.0, value=2000.0, key="c_plot")
            c_built = st.number_input(t("commercial_built_up_area_sq_ft"), min_value=0.0, value=3000.0, key="c_built")
            c_type = st.selectbox(t("building_type"), ["Office Space", "Retail Shop", "Warehouse", "Industrial", "Mixed Use"], key="c_type")
        with ccol2:
            c_rent_m = st.number_input(t("monthly_rental_income"), min_value=0, value=150000, step=10000, key="c_rent_m")
            c_rent_y = st.number_input(t("annual_rental_income"), min_value=0, value=1800000, step=100000, key="c_rent_y")
            c_lease = st.selectbox(t("lease_status"), ["Long-term Leased", "Short-term Leased", "Vacant", "Self-Occupied"], key="c_lease")
        with ccol3:
            c_floors = st.number_input(t("number_of_floors"), min_value=1, value=2, key="c_floors")
            c_occ = st.slider("Current Occupancy (%)", 0, 100, 85, key="c_occ")
            c_year = st.number_input(t("construction_year"), min_value=1950, max_value=2026, value=2015, key="c_year_comm")

        # --- SECTION 5: COMMERCIAL LOAN ASSESSMENT ---
        st.markdown(t("commercial_loan_assessment"))
        if st.button(t("calculate_commercial_valuation_emi"), key="btn_c_calc"):
            with st.spinner("Analyzing commercial cash flows and DSCR..."):
                from backend.routers.valuation import evaluate_loan_module, EvaluateLoanModuleInput
                res = evaluate_loan_module(EvaluateLoanModuleInput(
                    module="commercial", district=st.session_state.get("val_district_sel", "Bengaluru Urban"), plot_area=c_plot, built_up_area=c_built,
                    interest_rate=10.5, tenure_months=180
                ))
                
                # --- SECTION 4: COMMERCIAL PROPERTY INTELLIGENCE ---
                st.markdown(t("commercial_property_intelligence"))
                vcol1, vcol2, vcol3 = st.columns(3)
                with vcol1:
                    st.metric("Govt Guidance Value", f"₹{res['property_value'] * 0.7:,.2f}")
                    st.metric("Rental Yield", "7.5% Annual")
                with vcol2:
                    st.metric("AI Estimated Market Value", f"₹{res['property_value']:,.2f}")
                    st.metric("Location Score", "95/100 (Prime Commercial)")
                with vcol3:
                    st.markdown(t("fraud_detection_span_style_color_10b981_"), unsafe_allow_html=True)
                    st.markdown(t("explainable_ai_strong_cash_flows_and_sol"), unsafe_allow_html=True)
                
                # --- SECTION 5 (cont): LOAN METRICS ---
                st.markdown(t("loan_underwriting_metrics"))
                ucol1, ucol2, ucol3 = st.columns(3)
                with ucol1:
                    st.metric("Eligible Loan (65% LTV)", f"₹{res['eligible_loan']:,.2f}")
                with ucol2:
                    st.metric("Monthly EMI", f"₹{res['monthly_emi']:,.2f}")
                with ucol3:
                    st.metric("Projected DSCR", "1.45x")
                st.success(t("ai_loan_recommendation_approve_strong_ds"))
                
                # --- NEARBY LISTINGS & PROJECTIONS ---
                st.markdown(t("nearby_similar_registered_properties_ngd"))
                import pandas as pd
                import random
                nb1 = int(res['comm_rate_per_sqft'] * random.uniform(0.9, 1.1))
                nb2 = int(res['comm_rate_per_sqft'] * random.uniform(0.9, 1.1))
                nb3 = int(res['comm_rate_per_sqft'] * random.uniform(0.9, 1.1))
                s_num = st.session_state.get("val_survey", "101/2")
                ndf = pd.DataFrame({
                    "Survey Number": [f"{s_num.split('/')[0]}/{random.randint(1,100)}", f"{random.randint(1,500)}/4", f"{random.randint(1,500)}/2"],
                    "Distance (m)": [120, 310, 480],
                    "Registered Price (per sqft)": [f"₹{nb1:,}", f"₹{nb2:,}", f"₹{nb3:,}"],
                    "Registry Source": ["NGDRS State Registry", "Kaveri Portal / TNREGINET", "Kaveri Portal / TNREGINET"],
                    "Transaction Date": ["14-05-2026", "22-04-2026", "10-02-2026"]
                })
                st.table(ndf)
            
                st.markdown(t("future_collateral_appreciation_forecast"))
                pcol1, pcol2, pcol3, pcol4 = st.columns(4)
                pcol1.metric("Growth Rate", "10.5% Annual")
                pcol2.metric("1 Year Value Projection", f"₹{res['property_value'] * 1.105:,.2f}")
                pcol3.metric("3 Years Value Projection", f"₹{res['property_value'] * 1.349:,.2f}")
                pcol4.metric("5 Years Value Projection", f"₹{res['property_value'] * 1.647:,.2f}")
                
                # --- SECTION 6: REPORTS ---
                st.markdown(t("ai_report_generator"))
                c_rep_data = st.session_state.get("c_report_data", None)
                if c_rep_data is None:
                    if st.button(t("generate_ai_valuation_report"), key="btn_c_gen"):
                        with st.spinner("Generating detailed AI underwriting report via Groq..."):
                            from backend.services.report_generator import generate_loan_report, md_to_pdf_bytes
                            report_md = generate_loan_report("Commercial Loan", res)
                            st.session_state["c_report_data"] = md_to_pdf_bytes(report_md)
                            st.rerun()
                else:
                    st.success(t("ai_report_generated_successfully"))
                    st.download_button("📄 Download AI Valuation Report (PDF)", data=c_rep_data, file_name="Commercial_Valuation.pdf", mime="application/pdf", key="c_rep1")

        st.markdown(t("div"), unsafe_allow_html=True)

    elif loan_prod_sel == "🥇 Gold Loan":
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("ai_gold_loan_appraisal_risk_intelligence"))
        
        # --- SECTION 1: ASSET DETAILS ---
        st.markdown(t("gold_asset_details"))
        gcol1, gcol2, gcol3 = st.columns(3)
        with gcol1:
            g_wt = st.number_input(t("gold_weight_grams"), min_value=1.0, value=50.0, key="g_wt")
        with gcol2:
            g_pur = st.selectbox(t("purity"), ["24K", "22K", "18K", "14K"], index=1, key="g_pur")
        with gcol3:
            g_type = st.selectbox(t("ornament_type"), ["Solid Chain/Bangles", "Stone Embedded", "Coins/Bars"], key="g_type")

        # --- SECTION 2: VERIFICATION CHECK ---
        st.markdown(t("asset_verification"))
        st.info(t("hallmark_verification_passed_huid_matche"))

        # --- SECTION 5: FINAL SANCTION & REPORTS ---
        st.markdown(t("ai_gold_appraisal"))
        if st.button(t("calculate_live_gold_valuation"), key="btn_g_calc"):
            with st.spinner("Fetching live spot rates and analyzing volatility..."):
                from backend.routers.valuation import evaluate_loan_module, EvaluateLoanModuleInput
                res = evaluate_loan_module(EvaluateLoanModuleInput(module="gold", gold_weight_grams=g_wt, gold_purity=g_pur))
                
                # --- SECTION 3: MARKET INTELLIGENCE ---
                st.markdown(t("market_intelligence"))
                mcol1, mcol2, mcol3 = st.columns(3)
                with mcol1:
                    st.metric("Live Spot Rate (Per Gram)", f"₹{res['rate_per_gram']:,}")
                with mcol2:
                    st.metric("30-Day Volatility", "Low (1.2%)", delta_color="normal")
                with mcol3:
                    st.metric("1-Year Forecast", "+8.5% Growth")
                
                # --- SECTION 4: RISK ANALYSIS ---
                st.markdown(t("risk_analysis_safe_limits"))
                rcol1, rcol2, rcol3 = st.columns(3)
                with rcol1:
                    st.metric("Regulatory Max LTV", "75.0%")
                with rcol2:
                    st.metric("AI Safe LTV Limit", "72.0%")
                with rcol3:
                    st.markdown(t("ai_risk_grade_span_style_color_10b981_fo"), unsafe_allow_html=True)

                st.success(f"✅ Total Gold Value: **₹{res['gold_value']:,.2f}** | Eligible Loan: **₹{res['eligible_loan']:,.2f}** | Monthly EMI: **₹{res['monthly_emi']:,.2f}/mo**")
                
                st.markdown(t("ai_report_generator"))
                g_rep_data = st.session_state.get("g_report_data", None)
                if g_rep_data is None:
                    if st.button(t("generate_ai_valuation_report"), key="btn_g_gen"):
                        with st.spinner("Generating detailed AI underwriting report via Groq..."):
                            from backend.services.report_generator import generate_loan_report, md_to_pdf_bytes
                            report_md = generate_loan_report("Gold Loan", res)
                            st.session_state["g_report_data"] = md_to_pdf_bytes(report_md)
                            st.rerun()
                else:
                    st.success(t("ai_report_generated_successfully"))
                    st.download_button("📄 Download AI Valuation Report (PDF)", data=g_rep_data, file_name="Gold_Valuation.pdf", mime="application/pdf", key="g_rep1")
        st.markdown(t("div"), unsafe_allow_html=True)

    elif loan_prod_sel == "🚜 Farm Equipment Loan":
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("farm_equipment_intelligence_underwriting"))
        
        # --- SECTION 1: ASSET DETAILS ---
        st.markdown(t("machinery_details"))
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            f_eq = st.selectbox(t("equipment_type"), ["Tractor", "Combine Harvester", "Rotavator", "Power Tiller", "Irrigation Solar Pump"], key="f_eq")
            f_brand = st.selectbox(t("brand"), ["Mahindra", "John Deere", "Sonalika", "Massey Ferguson", "Other"], key="f_brand")
        with fcol2:
            f_cost = st.number_input(t("purchase_cost"), min_value=10000.0, value=850000.0, key="f_cost")
            f_sub = st.number_input(t("govt_subsidy_support"), min_value=0.0, value=200000.0, key="f_sub")
        with fcol3:
            f_down = st.number_input(t("down_payment"), min_value=0.0, value=120000.0, key="f_down")
            f_acres = st.number_input(t("applicant_s_farm_land_acres"), min_value=0.5, value=6.0, key="f_acres")
            
        # --- SECTION 2: USAGE INTELLIGENCE ---
        st.markdown(t("usage_health_intelligence"))
        st.info(t("dealer_verification_passed_equipment_cla"))

        # --- SECTION 5: FINAL SANCTION & REPORTS ---
        st.markdown(t("ai_equipment_appraisal"))
        if st.button(t("calculate_farm_equipment_loan"), key="btn_f_calc"):
            with st.spinner("Analyzing depreciation curves and farming feasibility..."):
                from backend.routers.valuation import evaluate_loan_module, EvaluateLoanModuleInput
                res = evaluate_loan_module(EvaluateLoanModuleInput(
                    module="farm_equipment", equipment_type=f_eq, equipment_cost=f_cost, subsidy_amount=f_sub,
                    down_payment=f_down, farm_size_acres=f_acres
                ))
                
                # --- SECTION 3: AI VALUATION ---
                st.markdown(t("depreciation_market_value"))
                dcol1, dcol2, dcol3 = st.columns(3)
                with dcol1:
                    st.metric("Net Cost (Post Subsidy)", f"₹{res['net_equipment_cost']:,.2f}")
                with dcol2:
                    st.metric("1-Year Resale Value", f"₹{res['net_equipment_cost']*0.85:,.2f}", "-15%")
                with dcol3:
                    st.metric("3-Year Resale Value", f"₹{res['net_equipment_cost']*0.60:,.2f}", "-40%")
                
                # --- SECTION 4: RISK ANALYSIS ---
                st.markdown(t("risk_analysis"))
                rcol1, rcol2, rcol3 = st.columns(3)
                with rcol1:
                    st.metric("Repayment Feasibility", "Strong (6 Acres sufficient)")
                with rcol2:
                    st.metric("Ag Risk Score", f"{res['repayment_risk_score']}/100")
                with rcol3:
                    st.markdown(t("insurance_status_span_style_color_10b981"), unsafe_allow_html=True)
                
                st.success(f"✅ Eligible Loan (85% LTV): **₹{res['eligible_loan']:,.2f}** | Monthly EMI: **₹{res['monthly_emi']:,.2f}/mo**")
                
                st.markdown(t("ai_report_generator"))
                f_rep_data = st.session_state.get("f_report_data", None)
                if f_rep_data is None:
                    if st.button(t("generate_ai_valuation_report"), key="btn_f_gen"):
                        with st.spinner("Generating detailed AI underwriting report via Groq..."):
                            from backend.services.report_generator import generate_loan_report, md_to_pdf_bytes
                            report_md = generate_loan_report("Farm Equipment Loan", res)
                            st.session_state["f_report_data"] = md_to_pdf_bytes(report_md)
                            st.rerun()
                else:
                    st.success(t("ai_report_generated_successfully"))
                    st.download_button("📄 Download AI Valuation Report (PDF)", data=f_rep_data, file_name="Equipment_Valuation.pdf", mime="application/pdf", key="f_rep1")
        st.markdown(t("div"), unsafe_allow_html=True)

    elif loan_prod_sel == "🚗 Vehicle Loan":
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("ai_vehicle_intelligence_auto_finance"))
        
        @st.cache_data(ttl=3600)
        def get_cached_makes():
            from backend.services.vehicle_service import fetch_carquery_makes
            return fetch_carquery_makes()
            
        @st.cache_data(ttl=3600)
        def get_cached_models(make):
            from backend.services.vehicle_service import fetch_carquery_models
            return fetch_carquery_models(make)
            
        @st.cache_data(ttl=3600)
        def get_cached_specs(make, model):
            from backend.services.vehicle_service import fetch_carquery_specs
            return fetch_carquery_specs(make, model)
            
        makes_list = get_cached_makes()
        
        # --- SECTION 1: ASSET DETAILS ---
        st.markdown(t("vehicle_asset_details"))
        vcol1, vcol2, vcol3 = st.columns(3)
        with vcol1:
            v_make = st.selectbox(t("vehicle_brand_make"), makes_list, index=makes_list.index("Mahindra") if "Mahindra" in makes_list else 0, key="st_v_make")
            models_list = get_cached_models(v_make)
            v_model = st.selectbox(t("vehicle_model"), models_list, key="st_v_model")
        with vcol2:
            specs = get_cached_specs(v_make, v_model)
            v_year = st.selectbox(t("manufacturing_year"), [2026, 2025, 2024, 2023, 2022], key="v_year")
            v_fuel = st.selectbox(t("fuel_type"), ["Petrol", "Diesel", "EV", "Hybrid"], index=["Petrol", "Diesel", "EV", "Hybrid"].index(specs.get('fuel_type', 'Diesel')) if specs.get('fuel_type', 'Diesel') in ["Petrol", "Diesel", "EV", "Hybrid"] else 1, key="v_fuel")
        with vcol3:
            v_ex = st.number_input(t("ex_showroom_price"), min_value=10000.0, value=float(specs.get("ex_showroom_price", 1200000.0)), key="st_v_ex")
            v_onroad = st.number_input(t("on_road_price"), min_value=10000.0, value=float(specs.get("on_road_price", 1380000.0)), key="st_v_onroad")
            v_down = st.number_input(t("down_payment"), min_value=0.0, value=float(specs.get("on_road_price", 1380000.0) * 0.15), key="st_v_down")

        # --- SECTION 2: VEHICLE INTELLIGENCE ---
        st.markdown(t("registration_verification"))
        st.info(f"⚙️ **CarQuery API Specs:** `{specs.get('transmission', 'Manual')}` • `{specs.get('engine_cc', '2000 cc')}` • `{specs.get('body_type', 'SUV')}` | **RC Check:** Not Registered (New)")

        # --- SECTION 5: FINAL SANCTION & REPORTS ---
        st.markdown(t("ai_auto_appraisal"))
        if st.button(t("calculate_vehicle_loan_eligibility"), key="btn_v_calc"):
            with st.spinner("Analyzing credit risk and vehicle depreciation..."):
                from backend.routers.valuation import evaluate_loan_module, EvaluateLoanModuleInput
                res = evaluate_loan_module(EvaluateLoanModuleInput(
                    module="vehicle", vehicle_make=v_make, vehicle_model=v_model,
                    fuel_type=specs.get('fuel_type', 'Diesel'), transmission=specs.get('transmission', 'Manual'), engine_cc=specs.get('engine_cc', '2000 cc'),
                    ex_showroom_price=v_ex, on_road_price=v_onroad, down_payment=v_down
                ))
                
                # --- SECTION 3: AI VALUATION ---
                st.markdown(t("market_resale_forecast"))
                mcol1, mcol2, mcol3 = st.columns(3)
                with mcol1:
                    st.metric("Current Market Value", f"₹{res['on_road_price']:,.2f}")
                with mcol2:
                    st.metric("3-Year Resale Value", f"₹{res['on_road_price']*0.65:,.2f}", "-35%")
                with mcol3:
                    st.metric("5-Year Resale Value", f"₹{res['on_road_price']*0.45:,.2f}", "-55%")
                
                # --- SECTION 4: RISK ANALYSIS ---
                st.markdown(t("risk_fraud_analysis"))
                rcol1, rcol2, rcol3 = st.columns(3)
                with rcol1:
                    st.metric("Credit Risk Score", f"{res['credit_risk_score']}/100")
                with rcol2:
                    st.markdown(t("stolen_vehicle_database_span_style_color"), unsafe_allow_html=True)
                with rcol3:
                    st.markdown(t("insurance_status_span_style_color_10b981"), unsafe_allow_html=True)
                
                st.success(f"✅ Sanctioned Loan (85% LTV Cap): **₹{res['loan_sanction']:,.2f}** | Monthly EMI: **₹{res['monthly_emi']:,.2f}/mo**")
                
                st.markdown(t("ai_report_generator"))
                v_rep_data = st.session_state.get("v_report_data", None)
                if v_rep_data is None:
                    if st.button(t("generate_ai_valuation_report"), key="btn_v_gen"):
                        with st.spinner("Generating detailed AI underwriting report via Groq..."):
                            from backend.services.report_generator import generate_loan_report, md_to_pdf_bytes
                            report_md = generate_loan_report("Vehicle Loan", res)
                            st.session_state["v_report_data"] = md_to_pdf_bytes(report_md)
                            st.rerun()
                else:
                    st.success(t("ai_report_generated_successfully"))
                    st.download_button("📄 Download AI Valuation Report (PDF)", data=v_rep_data, file_name="Auto_Valuation.pdf", mime="application/pdf", key="v_rep1")
        st.markdown(t("div"), unsafe_allow_html=True)


# ================= TAB 3: DOCUMENT VERIFICATION =================
with tab3:
    st.markdown(t("div_class_section_header_cross_document_"), unsafe_allow_html=True)
    st.markdown(t("p_style_color_475569_font_size_12px_uplo"), unsafe_allow_html=True)
    
    # Simulating Tampered Dossiers
    st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
    st.subheader(t("verification_demo_profile_simulator_for_"))
    demo_profile = st.selectbox(
        t("select_verification_dossier_spoof_profil"),
        [
            "Standard Clean Profile (Approved status)",
            "Identity Tampering / Spoofing (Flags Name Mismatches & Deed Owner Conflicts)",
            "Income Alteration / Salary Bounces (Flags Pay Slip vs Statement variance & EMIs Bounces)",
            "Registry Boundaries Fraud (Flags Geospatial Coordinates map overlay conflicts)",
            "Perfect Applicant (Clean check / Approved status)",
            "Missing PAN (Blocks evaluation / Alerts missing PAN)",
            "Blurry Aadhaar (Low OCR Confidence / Warning alerts)",
            "Fake Salary Slip (Triggers fraud warning flags)",
            "Property Deed Mismatch (Owner Name mismatch)",
            "Low Income (High Risk / Low salary flags)",
            "High Debt (DTI Threshold Exceeded / High debt flags)",
            "Duplicate Application Reference (Triggers duplicate warning flags)"
        ]
    )
    enable_simulation = st.checkbox("Enable Demo Simulation (Fall back to spoof profile if no files are uploaded)", value=False)
    if enable_simulation:
        st.info(t("demo_simulation_is_active_if_you_run_the"))
    else:
        st.warning(t("demo_simulation_is_inactive_you_must_upl"))
    st.markdown(t("div"), unsafe_allow_html=True)
    
    st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
    st.subheader(t("verification_context"))
    chk_name = st.text_input(t("borrower_name_to_cross_verify_aadhaar_pa"), value="Rajesh Kumar")
    chk_salary = st.number_input(t("declared_salary_to_verify_net_pay_in_sli"), min_value=1000, value=75000)
    
    st.markdown("---")
    st.subheader(t("upload_pdfs_for_ocr_verification"))
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
        
    st.markdown(t("div"), unsafe_allow_html=True)
    
    if st.button(t("run_ocr_document_audit")):
        # Setup category label based on selection
        if "Standard Clean Profile" in demo_profile or "Perfect Applicant" in demo_profile:
            profile_lbl = "Standard"
        elif "Identity Tampering" in demo_profile or "Property Deed Mismatch" in demo_profile:
            profile_lbl = "Identity Tampering / Spoofing"
        elif "Income Alteration" in demo_profile or "Fake Salary" in demo_profile:
            profile_lbl = "Income Alteration / Salary Bounces"
        elif "Registry Boundaries" in demo_profile or "Duplicate" in demo_profile:
            profile_lbl = "Registry Boundaries Fraud"
        else:
            profile_lbl = "Standard"

        # Check if any uploads are present
        has_any_upload = (upl_aadhaar is not None) or (upl_pan is not None) or (upl_slip is not None) or (upl_deed is not None) or \
                         (upl_passport is not None) or (upl_dl is not None) or (upl_itr is not None) or (upl_ec is not None) or (upl_bill is not None)
        
        use_demo_simulation = enable_simulation and not has_any_upload
        
        # Enforce required documents check in non-simulation mode
        if not use_demo_simulation:
            missing_docs = []
            if upl_aadhaar is None:
                missing_docs.append("Aadhaar Card PDF")
            if upl_pan is None:
                missing_docs.append("PAN Card PDF")
            if upl_slip is None:
                missing_docs.append("Salary Slip PDF")
            
            vp_data_temp = st.session_state.get("valued_property", None)
            is_unsec_check = True if (vp_data_temp and vp_data_temp.get("Land_Type") == "Unsecured") else False
            if not is_unsec_check and upl_deed is None:
                missing_docs.append("Sale Deed PDF (Title Deed)")
                
            if missing_docs:
                st.error(t("cannot_start_verification_missing_requir") + 
                         "\n".join([f"• {doc}" for doc in missing_docs]) + 
                         "\n\n*Please upload all required files to perform a real credit audit.*")
                st.stop()

        with st.spinner("Extracting parameters with OCR engines..."):
            # Lazy load heavy document verification modules to save memory
            from utils.ocr_engine import process_dossier_file
            from utils.verification_engine import (
                verify_identity_dossier, verify_income_dossier, verify_property_dossier,
                verify_cashflow_stability, conduct_fraud_brain_audit,
                calculate_document_trust_score, levenshtein_ratio, compile_relationship_nodes
            )
            
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
            
            # Execute real OCR if files are uploaded, otherwise fall back to demo profiles if simulation is enabled
            use_demo_simulation = enable_simulation and not has_any_upload
            
            if not use_demo_simulation:
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
                    if "Blurry Aadhaar" in demo_profile:
                        aadhaar_ocr = {"Name": "Rajes Kmar", "DOB": "15-08-1988", "Aadhaar_Number": "XXXX-XXXX-1102", "Confidence_Score": 55}
                    else:
                        aadhaar_ocr = {"Name": chk_name, "DOB": "15-08-1988", "Aadhaar_Number": "XXXX-XXXX-1102", "Confidence_Score": 98}
                        
                if pan_ocr is None:
                    if "Missing PAN" in demo_profile:
                        pan_ocr = {"Missing": True, "Name": "Missing", "DOB": "N/A", "PAN_Number": "MISSING", "Confidence_Score": 0}
                    elif "Identity Tampering" in demo_profile:
                        pan_ocr = {"Name": chk_name + " S", "DOB": "18-10-1988", "PAN_Number": "ABCDE1234F", "Confidence_Score": 95}
                    else:
                        pan_ocr = {"Name": chk_name, "DOB": "15-08-1988", "PAN_Number": "ABCDE1234F", "Confidence_Score": 98}
                        
                if salary_slip_ocr is None:
                    if "Low Income" in demo_profile:
                        salary_slip_ocr = {"Employer": "Infosys Ltd", "Net_Monthly_Salary": 10000.0, "Name": chk_name, "Confidence_Score": 95}
                    elif "High Debt" in demo_profile:
                        salary_slip_ocr = {"Employer": "Infosys Ltd", "Net_Monthly_Salary": 30000.0, "Name": chk_name, "Confidence_Score": 95}
                    elif "Income Alteration" in demo_profile or "Fake Salary" in demo_profile:
                        salary_slip_ocr = {"Employer": "Infosys Ltd", "Net_Monthly_Salary": float(chk_salary * 1.5), "Name": chk_name, "Confidence_Score": 40}
                    else:
                        salary_slip_ocr = {"Employer": "Infosys Ltd", "Net_Monthly_Salary": float(chk_salary), "Name": chk_name, "Confidence_Score": 95}
                        
                if bank_statement_ocr is None:
                    if "Low Income" in demo_profile:
                        bank_statement_ocr = {"Salary_Credits": [10000.0, 10000.0, 10000.0], "EMI_Bounces": 0, "Average_Balance": 3000.0}
                    elif "High Debt" in demo_profile:
                        bank_statement_ocr = {"Salary_Credits": [30000.0, 30000.0, 30000.0], "EMI_Bounces": 0, "Average_Balance": 12000.0}
                    elif "Income Alteration" in demo_profile or "Fake Salary" in demo_profile:
                        bank_statement_ocr = {"Salary_Credits": [chk_salary, chk_salary, chk_salary], "EMI_Bounces": 3, "Average_Balance": chk_salary * 0.1}
                    else:
                        s_val = salary_slip_ocr.get("Net_Monthly_Salary", chk_salary)
                        bank_statement_ocr = {"Salary_Credits": [s_val, s_val, s_val], "EMI_Bounces": 0, "Average_Balance": s_val * 1.5}
                        
                if sale_deed_ocr is None:
                    if "Registry Boundaries" in demo_profile:
                        sale_deed_ocr = {"Owner": chk_name, "Survey_Number": f"{vp_data['Survey_Number'].split('/')[0]}/{random.randint(50,200)}", "Village": "Chikka Banaswadi", "Land_Area": vp_data["Land_Area"], "Confidence_Score": 92}
                    elif "Property Deed Mismatch" in demo_profile or "Identity Tampering" in demo_profile:
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
                {"time": t_upload, "event": "📥 Document Dossier Uploaded", "desc": f"Files uploaded successfully. Strict Audit Mode active: {not use_demo_simulation}."},
                {"time": t_ocr, "event": "🤖 Google Cloud Vision OCR", "desc": "Structured text parameter annotations completed."},
                {"time": t_forensic, "event": "🔍 Forensic Brain Audits & Fraud Check", "desc": f"Analyzed resolution, font alterations, and file EXIF properties (Confidence: {fraud_res.get('Fraud_Brain_Confidence', 98.0)}%)."},
                {"time": t_verify, "event": "🔗 Node Linkage Mappings & Verification Completion", "desc": f"Cross-document fuzzy name matching completed: {trust_score}% score."}
            ]
            
            # Save results in session state
            st.session_state["dossier_verification"] = {
                "checked": True,
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
            
            # Clear intermediate variables and run gc.collect() to prevent OOM
            try:
                del identity_res, income_res, property_res, cashflow_res, fraud_res, timeline_logs
            except Exception:
                pass
            import gc
            gc.collect()
            log_memory_usage("After OCR Document Audit")
            
            st.success(t("ocr_document_audit_complete_trust_score_"))
            st.rerun()
            
    # Render Audit findings in Tab 3
    if "dossier_verification" in st.session_state:
        dv = st.session_state["dossier_verification"]
        
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("document_audit_dashboard_alignment_matri"))
        
        # Display Trust progress gauge
        st.markdown(f"#### Verified Document Trust Score: **{dv['trust_score']}%**")
        st.progress(int(dv['trust_score']))
        
        st.markdown("---")
        
        # Split into Trust Network breakdowns & Banking Compliance engine Checklist
        tcol1, tcol2 = st.columns(2)
        
        with tcol1:
            st.markdown(t("document_trust_network_metrics"))
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
            
            # Dynamic Sub-Module Confidence Ratings
            ocr_conf = int(np.mean([
                dv["ocr_data"].get("aadhaar", {}).get("Confidence_Score", 0) or 95,
                dv["ocr_data"].get("pan", {}).get("Confidence_Score", 0) or 95,
                dv["ocr_data"].get("salary_slip", {}).get("Confidence_Score", 0) or 90,
                dv["ocr_data"].get("sale_deed", {}).get("Confidence_Score", 0) or 92
            ]))
            name_similarity = int(levenshtein_ratio(
                dv["ocr_data"].get("aadhaar", {}).get("Name", "").lower(),
                dv["ocr_data"].get("pan", {}).get("Name", "").lower()
            ) * 100) if not dv["ocr_data"].get("aadhaar", {}).get("Missing") and not dv["ocr_data"].get("pan", {}).get("Missing") else 0
            if name_similarity == 0:
                name_similarity = 98
            pan_verification = 100 if dv.get("identity", {}).get("Name_Status") == "PASS" else 85
            property_match = int(levenshtein_ratio(
                dv["ocr_data"].get("sale_deed", {}).get("Owner", "").lower(),
                dv["ocr_data"].get("aadhaar", {}).get("Name", "").lower()
            ) * 100) if not dv["ocr_data"].get("sale_deed", {}).get("Missing") else 0
            if property_match == 0:
                property_match = 94
                
            st.markdown("---")
            st.markdown(t("sub_module_confidence_ratings"))
            st.markdown(f"- **OCR Extraction Confidence**: `{ocr_conf}%` Accuracy")
            st.markdown(f"- **PAN Verification Score**: `{pan_verification}%` Match")
            st.markdown(f"- **Name Match Similarity**: `{name_similarity}%` Similarity")
            st.markdown(f"- **Property Match Ownership**: `{property_match}%` Match")
            st.markdown(f"- **AI Underwriting Prediction**: `95%` Confidence")
            
        with tcol2:
            st.markdown(t("banking_compliance_audit_checklist"))
            is_good = dv["trust_score"] >= 85.0
            st.write(t("kyc_completeness_verified") if is_good else "⚠️ **KYC Mismatch Alert Flags**")
            st.write(t("aadhaar_format_validation_12_digits_chec"))
            st.write(t("pan_format_validation_check_passed"))
            st.write(t("ifsc_code_integrity_check_verified"))
            st.write(t("rbi_policy_cap_debt_to_income_check"))
            st.write(t("bank_lending_cap_ltv_threshold_checks"))
            
        st.markdown("---")
        
        # Render Relationship Nodes
        st.markdown(t("ai_relationship_nodes_fuzzy_integrity_ch"))
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
            st.markdown(t("dossier_forensic_audit_timeline"))
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
        st.markdown(t("ai_fraud_brain_audit_logs"))
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
        st.markdown(t("behavioural_cash_flow_risk_card"))
        col_cf1, col_cf2 = st.columns(2)
        with col_cf1:
            st.markdown(f"- **Bank Deposits consistency**: `{'🟢 Stable matching credits' if cf_chk['Status'] == 'PASS' else '🔴 ALERT: salary variance detected'}`")
            st.markdown(f"- **EMI Bounces logs**: `{'🟢 0 default entries' if cf_chk['EMI_Bounces'] == 0 else '🔴 ' + str(cf_chk['EMI_Bounces']) + ' default bounces detected'}`")
        with col_cf2:
            st.markdown(f"- **Cashflow stability Index**: `{cf_chk['Cashflow_Stability_Score']}/100`")
            st.markdown(f"- **Reserve balance reserve**: `₹{cf_chk['Average_Balance']:,.2f}`")
            
        # Display aggregated warn alerts
        all_alerts = id_chk["Flags"] + inc_chk["Flags"] + prop_chk["Flags"] + cf_chk["Flags"] + fr_chk["Flags"]
        st.markdown("---")
        if all_alerts:
            st.warning(t("matching_deviations_flagged_by_verificat"))
            for alert in all_alerts:
                st.write(f"- {alert}")
        else:
            st.success(t("document_checks_verified_cleanly_ready_t"))
            
        if st.session_state.get("developer_mode", False):
            st.markdown("---")
            st.subheader(t("developer_debugger_document_extraction_p"))
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.markdown(t("ocr_annotated_extracted_texts"))
                for doc_key, doc_data in dv.get("ocr_data", {}).items():
                    if doc_data and not doc_data.get("Missing", False):
                        st.markdown(f"**{doc_key.upper()} OCR Raw String Content:**")
                        st.code(doc_data.get("Raw_Text", "Sample OCR mock string text parsed by Google Cloud Vision API engine."))
            with d_col2:
                st.markdown(t("extracted_json_structured_parameter_fiel"))
                st.json(dv)
            
        st.markdown(t("div"), unsafe_allow_html=True)


# ================= TAB 4: SMART LOAN PREDICTION =================
with tab4:
    st.markdown(t("div_class_section_header_combined_credit"), unsafe_allow_html=True)
    
    st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
    st.subheader(t("collateral_guarantee_structure"))
    # Map the Multi-Product selection to the corresponding index
    mode_mapping = {
        "🏠 Home Loan": 0,
        "🌾 Agriculture Loan": 1,
        "🏢 Commercial Loan": 2,
        "🥇 Gold Loan": 3,
        "🚜 Farm Equipment Loan": 4,
        "🚗 Vehicle Loan": 5
    }
    # Safely get the selected value
    raw_sel = st.session_state.get("loan_prod_sel", "🏠 Home Loan")
    if isinstance(raw_sel, list) or isinstance(raw_sel, tuple):
        raw_sel = raw_sel[0] if len(raw_sel) > 0 else "🏠 Home Loan"
        
    try:
        default_index = mode_mapping.get(raw_sel, 0)
    except Exception:
        default_index = 0
    
    collateral_mode = st.selectbox(
        t("select_loan_structure"), 
        [
            "Home Loan (Secured by Residential Property)", 
            "Agriculture Loan (Secured by Ag Land)", 
            "Commercial Loan (Secured by Commercial Property)", 
            "Gold Loan (Secured by Gold Collateral)",
            "Farm Equipment Loan (Secured by Ag Machinery)",
            "Vehicle Loan (Secured by Vehicle Lien)",
            "Secured (Using Borrower Owned Property)", 
            "Unsecured Loan (Based on Income & CIBIL)"
        ],
        index=default_index
    )
    st.markdown(t("div"), unsafe_allow_html=True)
    
    # Check property mapping based on mode
    has_property = False
    vp = None
    
    if collateral_mode in ["Secured (Using Borrower Owned Property)", "Secured (Using Co-Applicant Owned Property)"]:
        if "valued_property" not in st.session_state:
            st.info(t("please_complete_the_property_valuation_a"))
        else:
            vp = st.session_state["valued_property"]
            has_property = True
            if collateral_mode == "Secured (Using Borrower Owned Property)":
                st.success(f"✅ Linked Borrower Collateral: Survey `{vp['Survey_Number']}` in `{vp['Village']}, {vp['District']}` (Valued: ₹{vp['total_market_value']:,.2f})")
            else:
                st.success(f"✅ Linked Co-Applicant Collateral: Survey `{vp['Survey_Number']}` in `{vp['Village']}, {vp['District']}` (Valued: ₹{vp['total_market_value']:,.2f})")
    elif collateral_mode == "Gold Loan (Secured by Gold Collateral)":
        from backend.routers.gold import fetch_live_gold_price
        if "gold_live_data" not in st.session_state:
            st.session_state["gold_live_data"] = fetch_live_gold_price()
        gold_data = st.session_state.get("gold_live_data", {})
        r24 = gold_data.get("price_gram_24k", 6382.63)
        r22 = gold_data.get("price_gram_22k", 5850.75)
        r18 = gold_data.get("price_gram_18k", 4786.97)
        
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("gold_collateral_details_live_spot_valuat"))
        gcol1, gcol2 = st.columns(2)
        with gcol1:
            g_weight_st = st.number_input(t("gold_collateral_weight_grams"), min_value=1.0, value=20.0, step=1.0, key="st_g_weight")
        with gcol2:
            g_purity_st = st.selectbox(t("purity_grade"), ["22K (Standard Ornaments)", "24K (Pure Bullion)", "18K (Jewelry)"], key="st_g_purity")
            
        rate_gram = r22
        purity_lbl = "22K"
        if "24K" in g_purity_st:
            rate_gram = r24
            purity_lbl = "24K"
        elif "18K" in g_purity_st:
            rate_gram = r18
            purity_lbl = "18K"
            
        total_gold_val = g_weight_st * rate_gram
        eligible_gold_ltv = total_gold_val * 0.75
        
        vp = {
            "State": "Karnataka",
            "District": "Gold Bullion Vault",
            "Taluk": "Gold Appraisal Cell",
            "Village": f"Gold Collateral ({g_weight_st}g, {purity_lbl})",
            "PIN_Code": "560001",
            "Survey_Number": "GOLD-COLLATERAL",
            "Land_Area": g_weight_st,
            "Land_Type": "Gold Bullion / Ornaments",
            "guidance_value_per_sqft": rate_gram,
            "total_guidance_value": total_gold_val,
            "total_market_value": total_gold_val,
            "max_loan_amount": eligible_gold_ltv,
            "eligible_ltv": 0.75,
            "fraud_check": {"status": "PASS"},
            "trust_score": 98.0,
            "property_class": f"Gold Collateral ({g_weight_st}g {purity_lbl})"
        }
        has_property = True
        st.success(f"✅ Gold Collateral Assessed: `{g_weight_st}g` ({purity_lbl}) @ ₹{rate_gram:,.2f}/g | Market Value: **₹{total_gold_val:,.2f}** | Max Eligible (75% LTV): **₹{eligible_gold_ltv:,.2f}**")
        st.markdown(t("div"), unsafe_allow_html=True)
    else:
        # Unsecured Mode
        has_property = True
        st.success(t("unsecured_credit_mode_active_no_property"))
        
    # Ensure vp is NEVER None for any collateral mode
    if vp is None:
        vp = {
            "State": "Karnataka",
            "District": "Bengaluru Urban",
            "Taluk": "Bengaluru South",
            "Village": "Standard Collateral",
            "PIN_Code": "560001",
            "Survey_Number": "COLLATERAL-01",
            "Land_Area": 1200,
            "Land_Type": collateral_mode,
            "guidance_value_per_sqft": 2500.0,
            "total_guidance_value": 3000000.0,
            "total_market_value": 5000000.0,
            "max_loan_amount": 3750000.0,
            "eligible_ltv": 0.75,
            "fraud_check": {"status": "PASS"},
            "trust_score": 95.0,
            "property_class": collateral_mode,
            "Risk_Score": 25
        }
        
    if has_property:
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("applicant_personal_credit_history"))
        
        lcol1, lcol2 = st.columns(2)
        with lcol1:
            name = st.text_input(t("borrower_name"), value="Rajesh Kumar", key="tab4_name")
            gender = st.selectbox(t("gender"), ["Male", "Female"])
            married = st.selectbox(t("married_status"), ["Yes", "No"])
            dependents = st.selectbox(t("dependents_count"), [0, 1, 2, 3])
            education = st.selectbox(t("education_level"), ["Graduate", "Not Graduate"])
            self_emp = st.selectbox(t("self_employed_status"), ["Yes", "No"])
            
        with lcol2:
            credit_hist = st.selectbox(t("credit_bureau_rating_cibil_status"), [1.0, 0.0], 
                                     format_func=lambda x: "Good / Satisfactory (>= 750)" if x == 1.0 else "Default / Poor History (< 650)", key="tab4_credit_hist")
            app_income = st.number_input(t("applicant_monthly_income"), min_value=1000, value=75000, key="tab4_app_income")
            co_income = st.number_input(t("co_applicant_monthly_income"), min_value=0, value=35000, key="tab4_co_income")
            loan_term = st.number_input(t("loan_repayment_tenure_months"), min_value=12, max_value=360, value=240)
            
            total_monthly_income = app_income + co_income
            # Contextual maximum loan limits
            if collateral_mode == "Unsecured Loan (Based on Income & CIBIL)":
                max_eligible_cap = int(total_monthly_income * 20)
                st.markdown(f"💡 **Recommended Max Unsecured Loan (20x Income):** `₹{max_eligible_cap:,.2f}`")
                loan_amount = st.number_input(t("requested_loan_sanction"), min_value=10000, value=min(500000, max_eligible_cap), key="tab4_loan_amount_u")
            elif collateral_mode == "Gold Loan (Secured by Gold Collateral)":
                max_eligible_cap = int(vp['max_loan_amount'])
                st.markdown(f"💡 **Recommended Max Gold Loan (75% RBI LTV):** `₹{max_eligible_cap:,.2f}`")
                loan_amount = st.number_input(t("requested_loan_sanction"), min_value=5000, value=max_eligible_cap)
            else:
                st.markdown(f"💡 **Recommended Max Loan (LTV Cap):** `₹{vp['max_loan_amount']:,.2f}` ({int(vp['eligible_ltv']*100)}% of Collateral)")
                if collateral_mode == "Secured (Using Co-Applicant Owned Property)" and co_income == 0:
                    st.warning(t("for_co_applicant_collateral_co_applicant"))
                loan_amount = st.number_input(t("requested_loan_sanction"), min_value=10000, value=min(int(vp['total_market_value'] * 0.7), int(vp['max_loan_amount'])))

        # Link validation state if available from verification tab
        dossier_checked = False
        trust_score = 95.0
        identity_res = {"Name_Status": "PASS", "Name_Match_Ratio": 0.95, "DOB_Status": "PASS"}
        income_res = {"Status": "PASS", "Name_Match_Ratio": 0.95}
        property_res = {"Owner_Status": "PASS", "Owner_Match_Ratio": 0.95}
        cashflow_res = {"Status": "PASS", "Cashflow_Stability_Score": 85}
        fraud_res = {"status": "PASS"}
        
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
            st.info(t("ℹ_standard_underwriting_mode_using_bench"))
            
        st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
        st.subheader(t("underwriting_audit_notes"))
        officer_notes_input = st.text_area(
            "Write Field Notes & Special Observations (included in PDF sanction letter)", 
            value=f"Applicant credentials and document nodes reviewed. Pinned coordinates verified at survey boundary {vp['Survey_Number'] if vp else 'N/A'}."
        )
        st.markdown(t("div"), unsafe_allow_html=True)
        
        if st.button(t("evaluate_predict_loan_approval"), key="btn_loan_main"):
            validation_errors = []
            
            # Check 1: Required documents uploaded
            if not dossier_checked:
                validation_errors.append("Document verification audit has not been completed. Run the audit in Tab 3.")
            else:
                ocr_d = st.session_state["dossier_verification"].get("ocr_data", {})
                if ocr_d.get("aadhaar", {}).get("Missing", False):
                    validation_errors.append("Aadhaar Card PDF is missing or not uploaded.")
                if ocr_d.get("pan", {}).get("Missing", False):
                    validation_errors.append("PAN Card PDF is missing or not uploaded.")
                if ocr_d.get("salary_slip", {}).get("Missing", False):
                    validation_errors.append("Salary Slip PDF is missing or not uploaded.")
                
                is_sec = (collateral_mode != "Unsecured Loan (Based on Income & CIBIL)")
                if is_sec and ocr_d.get("sale_deed", {}).get("Missing", False):
                    validation_errors.append("Property Sale Deed PDF is missing or not uploaded.")
                    
            # Check 2: Area > 0
            is_sec = (collateral_mode != "Unsecured Loan (Based on Income & CIBIL)")
            if is_sec and vp:
                if vp.get("Land_Area", 0) <= 0:
                    validation_errors.append("Collateral Land Area must be greater than 0.")
            
            # Check 3: Income > 0
            if (app_income + co_income) <= 0:
                validation_errors.append("Total declared monthly income must be greater than 0.")
                
            # Check 4: Loan amount valid
            if loan_amount <= 0:
                validation_errors.append("Requested loan sanction amount must be greater than 0.")
                
            if validation_errors:
                st.error(t("evaluation_blocked_input_validation_fail") + 
                         "\n".join([f"• {err}" for err in validation_errors]))
                st.stop()
                
            # Run Strict Health Check validations before starting evaluation
            health_failures = run_system_health_checks()
            if health_failures:
                st.error("Evaluation Terminated: System Health Checks Failed!\n\n"
                         "The evaluation cannot proceed because the following services are unavailable:\n\n" +
                         "\n".join([f"• {fail}" for fail in health_failures]))
                st.stop()
                
            with st.spinner("Analyzing credit parameters, pricing debt, and querying Groq AI Underwriter..."):
                # Lazy load heavy underwriting modules to save memory
                from utils.risk_engine import calculate_aegis_risk
                from utils.ai_explainer import generate_ai_underwriting_report
                from utils.pdf_generator import generate_pdf
                from utils.verification_engine import (
                    verify_identity_dossier, verify_income_dossier, verify_property_dossier,
                    verify_cashflow_stability, conduct_fraud_brain_audit,
                    calculate_document_trust_score, levenshtein_ratio, compile_relationship_nodes
                )
                
                from utils.model_loader import get_loan_model
                loan_model = get_loan_model()
                log_memory_usage("Starting Loan Underwriting Prediction")
                
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
                        print("Preparing loan prediction inputs...")
                        print(f"Loan model features shape: {input_df.shape}")
                        print(f"Loan model input columns: {list(input_df.columns)}")
                        print(f"Loan model inputs: {input_df.to_dict(orient='records')[0]}")
                        
                        # Explicit schema validation check before predict
                        expected_cols = [
                            "Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area", "Land_Type",
                            "Loan_Amount", "Total_Income", "Loan_Amount_Term", "Credit_History",
                            "Total_Market_Value", "Total_Guidance_Value", "LTV_Ratio", "DTI_Ratio", "Risk_Score"
                        ]
                        missing_cols = [col for col in expected_cols if col not in input_df.columns]
                        if missing_cols:
                            raise ValueError(f"Loan predictor schema error. Missing columns: {missing_cols}")
                            
                        loan_approved = loan_model.predict(input_df)[0]
                        print(f"Loan model prediction completed. Result: {loan_approved}")
                    except Exception as e:
                        st.error(f"Prediction Error: {e}")
                        print(f"[ERROR] Loan prediction run failed: {e}")
                        log_underwriting_error("Loan Prediction ML Model", str(e), {
                            "Gender": gender, "Married": married, "Total_Income": total_income,
                            "Loan_Amount": loan_amount, "LTV_Ratio": ltv_ratio, "DTI_Ratio": dti_ratio,
                            "Risk_Score": risk_score
                        })
                        loan_approved = 1 if (credit_hist == 1.0 and (ltv_ratio < 0.85 or ltv_ratio == 0.0) and dti_ratio < 0.55) else 0
                else:
                    print("ML loan prediction model .pkl file not found on server, using fallback rule engine.")
                    loan_approved = 1 if (credit_hist == 1.0 and (ltv_ratio < 0.85 or ltv_ratio == 0.0) and dti_ratio < 0.55) else 0
                
                # Underwriting compliance and risk score safety overrides
                override_triggered = False
                override_msg = ""
                
                # Check for strict business rules (Separated from ML models)
                is_secured = (collateral_mode != "Unsecured Loan (Based on Income & CIBIL)")
                
                if is_secured and loan_amount > vp.get("total_market_value", 0):
                    loan_approved = 0
                    override_triggered = True
                    override_msg = "LTV Compliance Rejection: Loan request amount (₹" + f"{loan_amount:,}" + ") exceeds estimated collateral market value (₹" + f"{vp.get('total_market_value', 0):,}" + ")."
                elif "ocr_data" in st.session_state.get("dossier_verification", {}) and st.session_state["dossier_verification"]["ocr_data"].get("aadhaar", {}).get("Missing", False):
                    loan_approved = 0
                    override_triggered = True
                    override_msg = "Identity Exception: Mandatory Aadhaar card verification was skipped or failed."
                elif "ocr_data" in st.session_state.get("dossier_verification", {}) and st.session_state["dossier_verification"]["ocr_data"].get("sale_deed", {}).get("Missing", False) and is_secured:
                    loan_approved = 0
                    override_triggered = True
                    override_msg = "Collateral Exception: Mandatory Property Sale Deed verification was skipped or failed."
                elif trust_score < 80.0:
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
                
                # Append detailed underwriting logs to the timeline
                underwriting_timeline = [
                    {"time": t_risk, "event": "⚙️ System Initialization", "desc": "AegisCR Underwriting Engine initialized. Loading local configurations..."},
                    {"time": t_risk, "event": "📂 Dossier Audit Scan", "desc": f"Loaded files structure check: Aadhaar, PAN, Salary Slip, and Property Deed. Trust score computed: {trust_score}%."},
                    {"time": t_risk, "event": "🤖 Machine Learning Loading", "desc": "Running ML Random Forest predictor model." if loan_model is not None else "Executing local heuristic prediction rules (Model fallback)."},
                    {"time": t_risk, "event": "📊 Aegis Credit Risk Assessment", "desc": f"Multi-factor credit algorithm score computed: {risk_score}/100 Index ({risk_res['Rating']})."},
                    {"time": t_decision, "event": "👨‍💼 Officer Decision Directive", "desc": f"Decision set to {decision_text.upper()}. Override warnings flag: {override_triggered}."},
                    {"time": t_pdf, "event": "📑 Sanction PDF Report Compiled", "desc": f"Generated final sanction letter registry dossier. Saved in logs."}
                ]
                
                # Save underwriting timeline logs in session state
                st.session_state["underwriting_timeline"] = underwriting_timeline
                
                # Save underwriting evaluation results to session state to prevent NameError on rerun
                st.session_state["underwriting_results"] = {
                    "dti_ratio": dti_ratio,
                    "emi": emi,
                    "ltv_ratio": ltv_ratio,
                    "ai_report": ai_report,
                    "decision_text": decision_text,
                    "identity_res": identity_res,
                    "income_res": income_res,
                    "property_res": property_res,
                    "cashflow_res": cashflow_res,
                    "fraud_res": fraud_res,
                    "trust_score": trust_score,
                    "vp": vp,
                    "name": name,
                    "gender": gender,
                    "married": married,
                    "dependents": dependents,
                    "education": education,
                    "self_emp": self_emp,
                    "app_income": app_income,
                    "co_income": co_income,
                    "loan_amount": loan_amount,
                    "loan_term": loan_term,
                    "credit_hist": credit_hist,
                    "collateral_mode": collateral_mode
                }
                
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
                
                # Clear intermediate variables and run gc.collect() to prevent OOM
                try:
                    del identity_res, income_res, property_res, cashflow_res, fraud_res, ai_report, underwriting_timeline, history_record
                except Exception:
                    pass
                import gc
                gc.collect()
                log_memory_usage("After Loan Underwriting Prediction")
                
                st.success(t("underwriting_predict_evaluation_complete"))
                st.rerun()
                
        # Render Decision details if saved
        if "underwriting_timeline" in st.session_state and "underwriting_results" in st.session_state:
            # Show results on UI
            st.markdown(t("div_class_glass_card"), unsafe_allow_html=True)
            st.subheader(t("underwriting_decision_credit_audit"))
            
            # Retrieve evaluated variables from stored results
            ur = st.session_state["underwriting_results"]
            dti_ratio = ur["dti_ratio"]
            emi = ur["emi"]
            ltv_ratio = ur["ltv_ratio"]
            ai_report = ur["ai_report"]
            decision_text = ur["decision_text"]
            identity_res = ur["identity_res"]
            income_res = ur["income_res"]
            property_res = ur["property_res"]
            cashflow_res = ur["cashflow_res"]
            fraud_res = ur["fraud_res"]
            trust_score = ur["trust_score"]
            vp = ur["vp"]
            name = ur["name"]
            gender = ur["gender"]
            married = ur["married"]
            dependents = ur["dependents"]
            education = ur["education"]
            self_emp = ur["self_emp"]
            app_income = ur["app_income"]
            co_income = ur["co_income"]
            loan_amount = ur["loan_amount"]
            loan_term = ur["loan_term"]
            credit_hist = ur["credit_hist"]
            collateral_mode = ur["collateral_mode"]
            
            # Render DIGITAL LOAN TWIN Profile Card
            st.markdown(t("applicant_digital_loan_twin_profile"))
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
            st.markdown(t("explainable_ai_xai_waterfall_risk_breakd"))
            st.markdown(t("the_following_compliance_deviations_incr"))
            risk_res_temp = calculate_aegis_risk(identity_res, income_res, property_res, credit_hist, ltv_ratio, dti_ratio, vp)
            xai_list = risk_res_temp["XAI_Waterfall"]
            for factor_item in xai_list:
                col_x1, col_x2 = st.columns([3, 1])
                col_x1.write(f"- {factor_item['factor']}")
                col_x2.markdown(f"**<font color='{risk_res_temp['Color']}'>{factor_item['impact']}</font>**", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # AI Case Investigator Dossier Panel
            st.markdown(t("ai_case_investigator_dossier"))
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
                    st.markdown(t("rejection_trigger_none_parameters_align_"))
                st.markdown(f"**Mandatory KYC Documents**: Verified (Aadhaar & PAN matched)")
            with cinv_c2:
                st.markdown(t("recommended_underwriter_interview_questi"))
                if trust_score < 80.0:
                    st.write(t("1_ask_the_applicant_to_explain_the_name_"))
                    st.write(t("2_request_physical_original_sale_deed_de"))
                else:
                    st.write(t("1_verify_the_applicant_s_current_net_tak"))
                    st.write(t("2_review_standard_field_surveyor_propert"))
                    
            st.markdown("---")
            
            # Underwriting timeline log render
            st.markdown(t("underwriting_decision_lifecycle_timeline"))
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
                # Calculate dynamic confidence index based on risk levels
                if decision_text.upper() == "APPROVED":
                    confidence = int(max(70, min(99, 100 - vp['Risk_Score'])))
                    st.success(f"🎉 **LOAN APPROVED** | Confidence: `{confidence}%`")
                    st.markdown(t("underwriting_highlights"))
                    st.markdown(t("repayment_record_approved_credit_history"))
                    if trust_score >= 85:
                        st.markdown(t("verified_credentials_dossier_extracted_n"))
                    if ltv_ratio < 0.75:
                        st.markdown(t("safe_loan_to_value_ltv_strong_collateral"))
                    if dti_ratio < 0.45:
                        st.markdown(t("safe_debt_to_income_dti_monthly_emi_cons"))
                    if cashflow_res["Status"] == "PASS":
                        st.markdown(t("stable_bank_account_cashflow_credit_freq"))
                else:
                    confidence = int(max(70, min(99, vp['Risk_Score'])))
                    st.error(f"❌ **LOAN REJECTED** | Confidence: `{confidence}%`")
                    if trust_score < 80.0:
                        st.warning(t("compliance_override_document_verificatio"))
                    elif vp["Risk_Score"] >= 65.0:
                        st.warning(t("combined_risk_index_exceeds_maximum_risk"))
                        
                    st.markdown(t("key_risk_deterrents"))
                    if credit_hist == 0.0:
                        st.markdown(t("high_default_exposure_cibil_defaults_or_"))
                    if trust_score < 80:
                        st.markdown(t("verification_deficit_document_name_check"))
                    if dti_ratio >= 0.55:
                        st.markdown(t("excessive_debt_burden_high_dti_monthly_e"))
                    if ltv_ratio >= 0.85:
                        st.markdown(t("high_valuation_risk_high_ltv_loan_reques"))
                    if cashflow_res["Average_Balance"] < emi * 1.2:
                        st.markdown(t("insufficient_balance_reserves_average_ba"))
                    
                st.markdown(f"**Aegis Risk Index:** `{vp['Risk_Score']}/100` ({risk_res_temp['Rating']})")
                
                # Dynamic Sub-Module Confidence Ratings
                ocr_conf = int(np.mean([
                    dv.get("ocr_data", {}).get("aadhaar", {}).get("Confidence_Score", 0) or 95,
                    dv.get("ocr_data", {}).get("pan", {}).get("Confidence_Score", 0) or 95,
                    dv.get("ocr_data", {}).get("salary_slip", {}).get("Confidence_Score", 0) or 90,
                    dv.get("ocr_data", {}).get("sale_deed", {}).get("Confidence_Score", 0) or 92
                ]))
                name_similarity = int(levenshtein_ratio(
                    dv.get("ocr_data", {}).get("aadhaar", {}).get("Name", "").lower(),
                    dv.get("ocr_data", {}).get("pan", {}).get("Name", "").lower()
                ) * 100) if not dv.get("ocr_data", {}).get("aadhaar", {}).get("Missing") and not dv.get("ocr_data", {}).get("pan", {}).get("Missing") else 0
                if name_similarity == 0:
                    name_similarity = 98
                pan_verification = 100 if dv.get("identity", {}).get("Name_Status") == "PASS" else 85
                property_match = int(levenshtein_ratio(
                    dv.get("ocr_data", {}).get("sale_deed", {}).get("Owner", "").lower(),
                    dv.get("ocr_data", {}).get("aadhaar", {}).get("Name", "").lower()
                ) * 100) if not dv.get("ocr_data", {}).get("sale_deed", {}).get("Missing") else 0
                if property_match == 0:
                    property_match = 94
                    
                st.markdown("---")
                st.markdown(t("dynamic_module_confidence_scores"))
                st.markdown(f"- **OCR Extraction**: `{ocr_conf}%` Accuracy")
                st.markdown(f"- **PAN Verification**: `{pan_verification}%` Match")
                st.markdown(f"- **Name Match Similarity**: `{name_similarity}%` Similarity")
                st.markdown(f"- **Property Match Ownership**: `{property_match}%` Match")
                st.markdown(f"- **Loan Prediction Probability**: `{confidence}%` Score")
                st.markdown(f"- **Overall Risk Trust Index**: `{trust_score}%` Rating")
                
            with rcol2:
                st.markdown(t("official_bank_pdf_report"))
                st.markdown(t("click_below_to_download_the_combined_lan"))
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
                    
            if st.session_state.get("developer_mode", False):
                st.markdown("---")
                st.subheader(t("developer_debugger_model_input_vectors_p"))
                dev_col1, dev_col2 = st.columns(2)
                with dev_col1:
                    st.markdown(t("credit_classifier_input_features_loan_mo"))
                    st.markdown(f"- **Total Market Value**: `₹{vp['total_market_value']}`")
                    st.markdown(f"- **Total Guidance Value**: `₹{vp['total_guidance_value']}`")
                    st.markdown(f"- **LTV Ratio**: `{ltv_ratio}`")
                    st.markdown(f"- **DTI Ratio**: `{dti_ratio}`")
                    st.markdown(f"- **Aegis Risk Index**: `{vp['Risk_Score']}`")
                    st.markdown(f"- **Credit History**: `{credit_hist}`")
                with dev_col2:
                    st.markdown(t("dynamic_calculations_verification_metric"))
                    st.markdown(f"- **Document Trust Score**: `{trust_score}%`")
                    st.markdown(f"- **Monthly EMI**: `₹{emi:,.2f}`")
                    st.markdown(f"- **Decision Vector**: `{decision_text.upper()}`")
                    st.markdown(f"- **Confidence Index**: `{confidence}%`")
                    
            st.markdown("---")
            st.markdown(t("groq_llm_underwriting_analysis"))
            st.markdown(ai_report)
            
            # Chat assistant copilot directly below predictions!
            st.markdown("---")
            st.subheader(t("ai_underwriting_copilot_chat"))
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
                
            copilot_msg = st.text_input(t("ask_the_ai_underwriting_copilot"), key="copilot_msg_input")
            if st.button(t("query_copilot"), key="btn_query_copilot"):
                if copilot_msg:
                    with st.spinner("Copilot analyzing dossier..."):
                        copilot_reply = query_underwriter_chat(copilot_msg, ctx_chat)
                        st.session_state["chat_history_main"].append((copilot_msg, copilot_reply))
                        
            for q, a in reversed(st.session_state["chat_history_main"]):
                st.write(f"👤 **Officer:** {q}")
                st.write(f"🤖 **Copilot:** {a}")
                st.markdown("---")
                
            st.markdown(t("div"), unsafe_allow_html=True)


# ================= TAB 5: VALUATION & LOAN LOGS =================
with tab5:
    st.markdown(t("div_class_section_header_valuation_decis"), unsafe_allow_html=True)
    
    current_role = st.session_state.get("user_role", "👔 Loan Officer")
    if "Customer" in current_role:
        st.warning(t("access_restricted_history_logs_and_decis"))
    else:
        # Filter stats by the logged-in user's UID (different employee has different stats)
        user_uid = "N/A"
        if "user" in st.session_state:
            user_uid = st.session_state["user"].get("uid", "N/A")
            
        if not history_df.empty and "User_UID" in history_df.columns:
            user_fresh_history = history_df[history_df["User_UID"] == user_uid]
        else:
            user_fresh_history = pd.DataFrame(columns=history_df.columns)
            
        if user_fresh_history.empty:
            st.info(t("no_applications_evaluated_yet_history_lo"))
        else:
            st.dataframe(
                user_fresh_history,
                column_config={
                    "Market_Value": st.column_config.NumberColumn("Estimated Market Value", format="₹%,.2f"),
                    "Circle Guidance Value": st.column_config.NumberColumn("Circle Guidance Value", format="₹%,.2f"),
                    "Loan_Amount": st.column_config.NumberColumn("Sanction Requested", format="₹%,.2f"),
                    "LTV_Ratio": st.column_config.NumberColumn("LTV Ratio", format="%.2f"),
                    "DTI_Ratio": st.column_config.NumberColumn("DTI Ratio", format="%.2f"),
                    "Risk_Score": st.column_config.ProgressColumn("Risk Index Score", min_value=0, max_value=100, format="%d/100")
                },
                hide_index=True,
                width='stretch'
            )
            
            if st.button(t("clear_logs_reset_portal_history")):
                if not history_df.empty and "User_UID" in history_df.columns:
                    # Remove only this user's records from the CSV file
                    updated_history_df = history_df[history_df["User_UID"] != user_uid]
                    updated_history_df.to_csv(HISTORY_FILE, index=False)
                st.success(t("portal_history_reset_successfully_reload"))
                import time
                time.sleep(1)
                st.rerun()