import os
from firebase_admin import db
from firebase.firebase_config import initialize_firebase

# Ensure Firebase is initialized
initialize_firebase()

def save_loan_application(uid, application_id, record):
    """
    Saves a loan application record in the Firebase Realtime Database.
    """
    try:
        ref = db.reference(f"loanApplications/{application_id}")
        # Insert User UID into record
        full_record = dict(record)
        full_record["User_UID"] = uid
        ref.set(full_record)
        return True
    except Exception as e:
        print(f"Error saving loan application to Firebase Database: {e}")
        return False
