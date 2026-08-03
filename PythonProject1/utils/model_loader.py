import streamlit as st
import os
import pickle
import gc

# Global in-memory cache for valuation and loan models
_cached_valuation_model = None
_cached_loan_model = None

@st.cache_resource
def get_valuation_model():
    """
    Lazy loads and caches the property valuation model.
    Works under both FastAPI and Streamlit contexts.
    """
    global _cached_valuation_model
    if _cached_valuation_model is not None:
        return _cached_valuation_model

    # Probe possible model binary locations
    model_paths = [
        "valuation_model.pkl",
        "PythonProject1/valuation_model.pkl",
        os.path.join(os.path.dirname(__file__), "..", "valuation_model.pkl"),
        os.path.join(os.path.dirname(__file__), "valuation_model.pkl")
    ]
    for path in model_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    model = pickle.load(f)
                gc.collect()
                _cached_valuation_model = model
                print(f"[MODEL LOADER] Successfully cached valuation model from {path}")
                return model
            except Exception as e:
                print(f"[ERROR] Failed to load valuation model from {path}: {e}")
    return None

@st.cache_resource
def get_loan_model():
    """
    Lazy loads and caches the loan approval model.
    Works under both FastAPI and Streamlit contexts.
    """
    global _cached_loan_model
    if _cached_loan_model is not None:
        return _cached_loan_model

    model_paths = [
        "loan_model.pkl",
        "PythonProject1/loan_model.pkl",
        os.path.join(os.path.dirname(__file__), "..", "loan_model.pkl"),
        os.path.join(os.path.dirname(__file__), "loan_model.pkl")
    ]
    for path in model_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    model = pickle.load(f)
                gc.collect()
                _cached_loan_model = model
                print(f"[MODEL LOADER] Successfully cached loan model from {path}")
                return model
            except Exception as e:
                print(f"[ERROR] Failed to load loan model from {path}: {e}")
    return None
