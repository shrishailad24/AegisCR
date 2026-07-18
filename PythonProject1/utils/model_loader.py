import os
import pickle
import streamlit as st
import gc

@st.cache_resource
def get_valuation_model():
    """
    Lazy loads and caches the property valuation model.
    """
    model_paths = ["valuation_model.pkl", "PythonProject1/valuation_model.pkl"]
    for path in model_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    model = pickle.load(f)
                gc.collect()
                return model
            except Exception as e:
                print(f"[ERROR] Failed to load valuation model from {path}: {e}")
    return None

@st.cache_resource
def get_loan_model():
    """
    Lazy loads and caches the loan approval model.
    """
    model_paths = ["loan_model.pkl", "PythonProject1/loan_model.pkl"]
    for path in model_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    model = pickle.load(f)
                gc.collect()
                return model
            except Exception as e:
                print(f"[ERROR] Failed to load loan model from {path}: {e}")
    return None
