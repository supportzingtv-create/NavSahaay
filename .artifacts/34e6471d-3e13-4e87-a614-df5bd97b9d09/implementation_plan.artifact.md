# Migration Plan: MySQL to Firebase Firestore

This plan outlines the steps to migrate the NavSahaay Flask application from a local MySQL database to Google Cloud Firestore (Firebase).

## User Review Required

> [!IMPORTANT]
> - **Firebase Service Account**: You will need to create a Firebase project, enable Firestore, and download a Service Account JSON key.
> - **Environment Variables**: The `FIREBASE_SERVICE_ACCOUNT_JSON` environment variable must be set in Vercel (and locally in `.env`) with the content of the service account file.
> - **ID Changes**: Firestore uses string document IDs. Some URLs that previously used integer IDs (like `/admin/donations/<int:id>/verify`) will be updated to use strings.

## Proposed Changes

### Dependencies & Configuration

#### [MODIFY] [requirements.txt](file:///Users/apple/AndroidStudioProjects/NavSahaay/requirements.txt)
- Add `firebase-admin`.
- Remove `Flask-SQLAlchemy`, `PyMySQL`, `Flask-Migrate`.

#### [MODIFY] [.env.example](file:///Users/apple/AndroidStudioProjects/NavSahaay/.env.example) and [.env](file:///Users/apple/AndroidStudioProjects/NavSahaay/.env)
- Remove `DATABASE_URL`.
- Add `FIREBASE_SERVICE_ACCOUNT_JSON`.

### Firebase Integration

#### [NEW] [firebase.py](file:///Users/apple/AndroidStudioProjects/NavSahaay/app/firebase.py)
- Initialize Firebase Admin SDK using the service account JSON from environment variables.
- Export the Firestore client (`db`).

#### [MODIFY] [__init__.py](file:///Users/apple/AndroidStudioProjects/NavSahaay/app/__init__.py)
- Remove SQLAlchemy and Migrate initialization.
- Import and initialize Firebase.

### Models Refactor

#### [MODIFY] [app/models/](file:///Users/apple/AndroidStudioProjects/NavSahaay/app/models/)
- Refactor all models (`User`, `Donation`, `Volunteer`, etc.) to use Firestore for persistence.
- Models will now act as Data Access Objects (DAOs) or simple data classes with static methods for Firestore queries.

### Routes & Services Update

#### [MODIFY] [app/routes/](file:///Users/apple/AndroidStudioProjects/NavSahaay/app/routes/)
- Update `auth.py`, `main.py`, `admin.py`, and `api.py` to use Firestore methods instead of `SQLAlchemy` queries.
- Update route parameters from `<int:id>` to `<string:id>` where applicable.

#### [MODIFY] [app/services/seed.py](file:///Users/apple/AndroidStudioProjects/NavSahaay/app/services/seed.py)
- Update seeding logic to work with Firestore.

## Verification Plan

### Automated Tests
- Run existing `pytest` suite (after updating tests to use Firestore mocks or a test database).

### Manual Verification
1. Start the Flask app locally.
2. Verify that the admin user is seeded into Firestore.
3. Test login/logout.
4. Test submitting a donation request and verifying it in the admin dashboard.
5. Test volunteer registration.
6. Test contact form submission.
7. Test event registration.
