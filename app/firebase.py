import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def get_db():
    if not firebase_admin._apps:
        # Get the JSON string from environment variable
        cert_data = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

        if not cert_data:
            # Fallback for local development if file exists
            cert_path = os.path.join(os.path.dirname(__file__), "..", "service-account.json")
            if os.path.exists(cert_path):
                cred = credentials.Certificate(cert_path)
            else:
                cred = credentials.ApplicationDefault()
        else:
            try:
                # Remove any potential whitespace or literal newlines that break JSON
                cert_data = cert_data.strip()

                # If the string contains literal \n instead of escaped newlines, fix it
                # This is a common issue when pasting JSON into environment variables
                cert_dict = json.loads(cert_data, strict=False)

                # Ensure private_key has correct newlines
                if "private_key" in cert_dict:
                    cert_dict["private_key"] = cert_dict["private_key"].replace("\\n", "\n")

                cred = credentials.Certificate(cert_dict)
            except Exception as e:
                print(f"Firebase Init Error: {e}")
                # Last resort fallback
                cred = credentials.ApplicationDefault()

        firebase_admin.initialize_app(cred)

    return firestore.client()

db = get_db()
