import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def get_db():
    if not firebase_admin._apps:
        cert_data = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

        if cert_data:
            try:
                # Clean the string from potential bad characters
                cert_data = cert_data.strip()
                cert_dict = json.loads(cert_data)

                # Fix private key newlines
                if "private_key" in cert_dict:
                    cert_dict["private_key"] = cert_dict["private_key"].replace("\\n", "\n")

                cred = credentials.Certificate(cert_dict)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"Firebase cert error: {e}")
                # Try loading without explicit credentials (for GCP/Firebase environments)
                firebase_admin.initialize_app()
        else:
            firebase_admin.initialize_app()

    return firestore.client()

# Initialize once
try:
    db = get_db()
except Exception as e:
    print(f"Firestore Client Error: {e}")
    db = None
