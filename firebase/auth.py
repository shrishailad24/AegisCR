import os
import requests
from firebase_admin import auth
from firebase.firebase_config import initialize_firebase

# Ensure Firebase is initialized
initialize_firebase()

# Web API Key for REST API operations
API_KEY = os.environ.get("FIREBASE_WEB_API_KEY", "AIzaSyBTRO62TZ4LDBL-ZcNY0GgzyoSZ-Ostlt4")

def sign_in_with_email(email, password):
    """
    Signs in a user with email and password via Firebase Auth REST API.
    Returns: (user_info_dict, error_message_or_None)
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        if response.status_code == 200:
            return res_data, None
        else:
            error_details = res_data.get("error", {})
            error_msg = error_details.get("message", "Unknown authentication error.")
            
            # User-friendly error messaging
            if error_msg in ["EMAIL_NOT_FOUND", "INVALID_PASSWORD", "INVALID_LOGIN_CREDENTIALS"]:
                return None, "Invalid email or password."
            elif error_msg == "USER_DISABLED":
                return None, "This user account has been disabled."
            elif error_msg == "TOO_MANY_ATTEMPTS_TRY_LATER":
                return None, "Too many login attempts. Please try again later."
            elif "PASSWORD_LOGIN_DISABLED" in error_msg or "ADMIN_ONLY_OPERATION" in error_msg or "Password login disabled" in error_msg:
                return None, "Email/Password sign-in is disabled in your Firebase console. Please go to your Firebase Console under Authentication > Sign-in method and enable the Email/Password provider."
            
            return None, error_msg.replace("_", " ").capitalize()
    except Exception as e:
        return None, f"Network error during authentication: {str(e)}"

def sign_up_with_email(email, password):
    """
    Registers a new user with email and password via Firebase Auth REST API.
    Returns: (user_info_dict, error_message_or_None)
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        if response.status_code == 200:
            return res_data, None
        else:
            error_details = res_data.get("error", {})
            error_msg = error_details.get("message", "Unknown registration error.")
            
            # User-friendly error messaging
            if error_msg == "EMAIL_EXISTS":
                return None, "This email address is already registered."
            elif "WEAK_PASSWORD" in error_msg:
                return None, "Password should be at least 6 characters long."
            elif "OPERATION_NOT_ALLOWED" in error_msg or "Password login disabled" in error_msg or "ADMIN_ONLY_OPERATION" in error_msg:
                return None, "Email/Password sign-up is disabled in your Firebase console. Please go to your Firebase Console under Authentication > Sign-in method and enable the Email/Password provider."
            
            return None, error_msg.replace("_", " ").capitalize()
    except Exception as e:
        return None, f"Network error during registration: {str(e)}"

def send_password_reset_email(email):
    """
    Sends a password reset link to the given email address.
    Returns: (success_boolean, error_message_or_None)
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        if response.status_code == 200:
            return True, None
        else:
            error_details = res_data.get("error", {})
            error_msg = error_details.get("message", "Unknown error sending reset email.")
            
            if error_msg == "EMAIL_NOT_FOUND":
                return False, "This email address is not registered."
            
            return False, error_msg.replace("_", " ").capitalize()
    except Exception as e:
        return False, f"Network error sending password reset: {str(e)}"

def verify_id_token(id_token):
    """
    Verifies the ID Token using the Admin SDK.
    Returns: (decoded_token_dict, error_message_or_None)
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token, None
    except Exception as e:
        return None, str(e)
