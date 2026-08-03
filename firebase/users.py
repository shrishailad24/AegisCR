import os
from datetime import datetime
from firebase_admin import db, auth
from firebase.firebase_config import initialize_firebase

# Ensure Firebase is initialized
initialize_firebase()

def save_user_profile(uid, name, email, photo_url=None, provider="Google", creation_time=None):
    """
    Saves/Updates user profile session data in the Firebase Realtime Database.
    """
    try:
        ref = db.reference(f"users/{uid}")
        
        # If creation_time is not provided, fetch from Firebase Auth metadata
        if not creation_time:
            try:
                user_record = auth.get_user(uid)
                creation_ms = user_record.user_metadata.creation_timestamp
                if creation_ms:
                    creation_time = datetime.fromtimestamp(creation_ms / 1000.0).isoformat()
                else:
                    creation_time = datetime.now().isoformat()
            except Exception:
                creation_time = datetime.now().isoformat()
        
        ref.set({
            "uid": uid,
            "name": name or "User",
            "email": email,
            "photoURL": photo_url or "",
            "lastLogin": datetime.now().isoformat(),
            "createdAt": creation_time,
            "provider": provider
        })
        return True
    except Exception as e:
        print(f"Error saving user profile to Firebase Database: {e}")
        return False
