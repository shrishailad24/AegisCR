import os
import firebase_admin
from firebase_admin import credentials

def load_env_file():
    """Manually load .env file to os.environ if present, avoiding external dependencies."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key_val = line.split("=", 1)
                        if len(key_val) == 2:
                            key = key_val[0].strip()
                            val = key_val[1].strip()
                            if val.startswith(('"', "'")) and val.endswith(('"', "'")):
                                val = val[1:-1]
                            os.environ[key] = val
        except Exception as e:
            print(f"Error loading .env file manually: {e}")

# Load env variables immediately on import
load_env_file()

def initialize_firebase():
    """Initializes the Firebase Admin SDK if it hasn't been initialized yet."""
    if not firebase_admin._apps:
        import json
        
        # 1. First, try to load from a JSON string in the environment (Best for Render/Heroku)
        service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
        database_url = os.environ.get("FIREBASE_DATABASE_URL", "https://aegiscr-b7b0e-default-rtdb.asia-southeast1.firebasedatabase.app")
        
        if service_account_json:
            try:
                # Parse the JSON string into a dictionary
                cred_dict = json.loads(service_account_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
                return True
            except Exception as e:
                print(f"Error initializing Firebase Admin from JSON env var: {e}")
                return False
                
        # 2. Fallback to file path (Local development)
        cert_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")
        if not cert_path:
            cert_path = os.path.join(os.path.dirname(__file__), "..", "credentials", "aegiscr-b7b0e-firebase-adminsdk.json")
        
        if os.path.exists(cert_path):
            try:
                cred = credentials.Certificate(cert_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
                return True
            except Exception as e:
                print(f"Error initializing Firebase Admin SDK from file: {e}")
                return False
        else:
            print(f"Firebase service account key not found at {cert_path} and FIREBASE_SERVICE_ACCOUNT_JSON not set.")
            return False
    return True

def get_firebase_status():
    """Returns True if Firebase Admin SDK is initialized successfully."""
    return len(firebase_admin._apps) > 0
