import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import r2_score, accuracy_score, classification_report

def train_models():
    # Load dataset
    df = pd.read_csv("property_loan_data.csv")
    print("Dataset loaded. Shape:", df.shape)
    
    # -------------------------------------------------------------
    # 1. TRAIN VALUATION REGRESSION MODEL
    # Target: Market_Value_Per_Sqft (much more stable to train than total value)
    # Features: State, District, Land_Type, Land_Area, Guidance_Value_Per_Sqft
    # -------------------------------------------------------------
    val_features = ["State", "District", "Land_Type", "Land_Area", "Guidance_Value_Per_Sqft"]
    val_target = "Market_Value_Per_Sqft"
    
    X_val = df[val_features]
    y_val = df[val_target]
    
    X_val_train, X_val_test, y_val_train, y_val_test = train_test_split(
        X_val, y_val, test_size=0.2, random_state=42
    )
    
    # Preprocessor for valuation
    cat_cols_val = ["State", "District", "Land_Type"]
    num_cols_val = ["Land_Area", "Guidance_Value_Per_Sqft"]
    
    val_preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols_val),
            ("num", StandardScaler(), num_cols_val)
        ]
    )
    
    # Pipeline
    val_pipeline = Pipeline([
        ("preprocessor", val_preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
    ])
    
    print("Training Valuation Model...")
    val_pipeline.fit(X_val_train, y_val_train)
    val_preds = val_pipeline.predict(X_val_test)
    val_r2 = r2_score(y_val_test, val_preds)
    print(f"Valuation Model R2 Score: {val_r2:.4f}")
    
    # Save valuation model
    with open("valuation_model.pkl", "wb") as f:
        pickle.dump(val_pipeline, f)
    print("Saved valuation_model.pkl")
    
    # -------------------------------------------------------------
    # 2. TRAIN LOAN APPROVAL CLASSIFICATION MODEL
    # Target: Loan_Approved
    # Features:
    # -------------------------------------------------------------
    loan_features = [
        "Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area", "Land_Type",
        "Loan_Amount", "Total_Income", "Loan_Amount_Term", "Credit_History",
        "Total_Market_Value", "Total_Guidance_Value", "LTV_Ratio", "DTI_Ratio", "Risk_Score"
    ]
    loan_target = "Loan_Approved"
    
    X_loan = df[loan_features]
    y_loan = df[loan_target]
    
    # Fill any NaNs just in case
    X_loan = X_loan.fillna({
        "Gender": "Male", "Married": "No", "Dependents": 0, "Education": "Graduate",
        "Self_Employed": "No", "Property_Area": "Semiurban", "Land_Type": "Residential",
        "Loan_Amount": 500000, "Total_Income": 50000, "Loan_Amount_Term": 360, "Credit_History": 1.0,
        "Total_Market_Value": 1000000, "Total_Guidance_Value": 500000, "LTV_Ratio": 0.5, "DTI_Ratio": 0.3,
        "Risk_Score": 30
    })
    
    X_loan_train, X_loan_test, y_loan_train, y_loan_test = train_test_split(
        X_loan, y_loan, test_size=0.2, random_state=42, stratify=y_loan
    )
    
    # Preprocessor for loan approval
    cat_cols_loan = ["Gender", "Married", "Education", "Self_Employed", "Property_Area", "Land_Type"]
    num_cols_loan = [
        "Dependents", "Loan_Amount", "Total_Income", "Loan_Amount_Term", "Credit_History",
        "Total_Market_Value", "Total_Guidance_Value", "LTV_Ratio", "DTI_Ratio", "Risk_Score"
    ]
    
    loan_preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols_loan),
            ("num", StandardScaler(), num_cols_loan)
        ]
    )
    
    # Pipeline
    loan_pipeline = Pipeline([
        ("preprocessor", loan_preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1))
    ])
    
    print("Training Loan Approval Model...")
    loan_pipeline.fit(X_loan_train, y_loan_train)
    loan_preds = loan_pipeline.predict(X_loan_test)
    loan_acc = accuracy_score(y_loan_test, loan_preds)
    print(f"Loan Approval Model Accuracy: {loan_acc:.4f}")
    print("\nClassification Report:\n", classification_report(y_loan_test, loan_preds))
    
    # Save loan approval model
    with open("loan_model.pkl", "wb") as f:
        pickle.dump(loan_pipeline, f)
    print("Saved loan_model.pkl")

if __name__ == "__main__":
    train_models()
