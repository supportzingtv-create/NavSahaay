# Shivoham Foundation — Flask + MySQL Local Full-Stack Project

This project is a **local-only full-stack implementation** based on the supplied Shivoham Website Strategy & Technical Specification.

## Stack

- Frontend: HTML + CSS + Jinja templates
- Backend: Flask
- ORM: Flask-SQLAlchemy
- Database: MySQL
- Driver: PyMySQL
- Authentication: Flask-Login
- CSRF protection: Flask-WTF
- PDF receipts: ReportLab
- Database migrations: Flask-Migrate
- Testing: pytest

## Intentionally excluded

No Razorpay, Cashfree, Stripe, UPI, card processing, deployment service, cloud storage, or external payment service is included.

The donation module records a **local donation request** in MySQL. It does not charge money.

## 1. Install Python

Use Python 3.11+.

Check:

```bash
python --version
```

## 2. Create the MySQL database

Start MySQL, then open MySQL Command Line Client or MySQL Workbench.

Run:

```sql
CREATE DATABASE shivoham CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

The application will create the tables automatically.

## 3. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install packages

```bash
pip install -r requirements.txt
```

## 5. Configure environment

Copy:

```text
.env.example
```

to:

```text
.env
```

Then change:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost:3306/shivoham
SECRET_KEY=your-local-secret
ADMIN_EMAIL=admin@shivoham.local
ADMIN_PASSWORD=Admin@123
```

If your MySQL root account has no password, use:

```env
DATABASE_URL=mysql+pymysql://root:@localhost:3306/shivoham
```

## 6. Run

```bash
python run.py
```

Open:

http://127.0.0.1:5000

## Admin

Open:

http://127.0.0.1:5000/login

Default local credentials:

```text
Email: admin@shivoham.local
Password: Admin@123
```

Change these in `.env` before using the project seriously.

## What works

### Public website

- Home
- About
- Programs
- Events
- Donation request form
- Volunteer registration
- Contact form
- Responsive design

### Backend

- MySQL persistence
- User authentication
- Role-based authorization
- Donations
- Donation verification
- Sequential local receipt number
- PDF receipt generation
- Volunteer records
- Volunteer status management
- Events CRUD
- Contact enquiries
- Document upload/download
- Basic JSON APIs
- CSRF protection
- Password hashing
- Audit log model

### API

```text
GET /api/events
GET /api/stats
```

## Database tables

The application creates:

```text
users
donations
volunteers
events
event_registrations
contacts
documents
audit_logs
```

## Important legal/data note

The supplied specification says not to publish unverified registration, PAN, 80G/12A/FCRA/CSR-1 details. Those values are deliberately not fabricated in this project.

Likewise, the local receipt generator is a technical prototype. It must not be represented as an official 80G tax receipt until Shivoham's actual legal/tax workflow is configured and verified.

## Next development stages

1. Replace placeholder legal/content data.
2. Add proper admin content editing for pages/programs.
3. Add event RSVP UI.
4. Add CSV export.
5. Add email notifications if desired.
6. Add search/filter/pagination to admin.
7. Add automated tests for all routes.
8. If later required, add a payment provider separately.
