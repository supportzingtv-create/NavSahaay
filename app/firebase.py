import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def get_db():
    if not firebase_admin._apps:
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if service_account_json:
            try:
                # Fix for common multiline issue in Vercel environment variables
                # Replace actual newlines with escaped newlines if needed
                if "\n" in service_account_json and "\\n" not in service_account_json:
                    # If it has literal newlines, it's not a valid single-line JSON string for some parsers
                    pass

                cred_dict = json.loads(service_account_json, strict=False)
                cred = credentials.Certificate(cred_dict)
            except Exception as e:
                # Fallback: if it's a path or complex string
                print(f"Firebase Init Error: {e}")
                try:
                    cred = credentials.Certificate(service_account_json)
                except:
                    cred = credentials.ApplicationDefault()
        else:
            cred = credentials.ApplicationDefault()

        firebase_admin.initialize_app(cred)

    return firestore.client()

db = get_db()
