import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def get_db():
    if not firebase_admin._apps:
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if service_account_json:
            try:
                # Try parsing as JSON string
                cred_dict = json.loads(service_account_json)
                cred = credentials.Certificate(cred_dict)
            except json.JSONDecodeError:
                # If not JSON, assume it's a path to a file
                cred = credentials.Certificate(service_account_json)
        else:
            # Fallback to default credentials if available (e.g., on GCP/Firebase environments)
            cred = credentials.ApplicationDefault()

        firebase_admin.initialize_app(cred)

    return firestore.client()

db = get_db()
