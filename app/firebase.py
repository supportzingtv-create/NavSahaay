import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def get_db():
    if not firebase_admin._apps:
        cert_data = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

        if cert_data:
            try:
                # Basic cleanup
                cert_data = cert_data.strip()

                # Try to parse the JSON
                cert_dict = json.loads(cert_data)

                # Fix private key if it's missing newlines
                if "private_key" in cert_dict:
                    cert_dict["private_key"] = cert_dict["private_key"].replace("\\n", "\n")

                cred = credentials.Certificate(cert_dict)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"Firebase Init Warning: {e}. Attempting default config.")
                try:
                    firebase_admin.initialize_app()
                except:
                    return None
        else:
            try:
                firebase_admin.initialize_app()
            except:
                return None

    try:
        return firestore.client()
    except:
        return None

# Attempt to initialize global db
db = None
try:
    db = get_db()
except Exception:
    db = None
