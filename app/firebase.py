import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def get_db():
    if not firebase_admin._apps:
        cert_data = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

        if cert_data:
            try:
                # Clean and parse JSON
                cert_data = cert_data.strip()
                # If it's wrapped in quotes by mistake during paste, remove them
                if cert_data.startswith('"') and cert_data.endswith('"'):
                    cert_data = cert_data[1:-1]

                # Replace literal escaped newlines with actual newlines
                cert_data = cert_data.replace("\\\\n", "\\n")

                cert_dict = json.loads(cert_data)

                # Fix private key newlines specifically
                if "private_key" in cert_dict:
                    # Handle both escaped and literal newlines
                    cert_dict["private_key"] = cert_dict["private_key"].replace("\\n", "\n")

                cred = credentials.Certificate(cert_dict)
                firebase_admin.initialize_app(cred)
                print("Firebase initialized successfully with service account.")
            except Exception as e:
                print(f"CRITICAL: Firebase Init Error: {e}")
                try:
                    # Attempt default initialization (might work on some cloud environments)
                    firebase_admin.initialize_app()
                    print("Firebase initialized with default credentials.")
                except Exception as e2:
                    print(f"CRITICAL: Firebase Default Init also failed: {e2}")
                    return None
        else:
            print("WARNING: FIREBASE_SERVICE_ACCOUNT_JSON not found in environment.")
            try:
                firebase_admin.initialize_app()
            except:
                return None

    return firestore.client()

# Global db object
db = None
try:
    db = get_db()
except Exception as e:
    print(f"Failed to create Firestore client: {e}")
