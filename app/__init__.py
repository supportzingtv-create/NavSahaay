import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Ensure SECRET_KEY is never None or empty
    secret = os.getenv("SECRET_KEY")
    if not secret:
        secret = "shivoham-fallback-secret-key-12345"

    app.config["SECRET_KEY"] = secret
    app.secret_key = secret

    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "..", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"

    # Subdomain Configuration
    server_name = os.getenv("SERVER_NAME")
    if server_name:
        app.config["SERVER_NAME"] = server_name
        app.config["SESSION_COOKIE_DOMAIN"] = f".{server_name}"
        app.config["REMEMBER_COOKIE_DOMAIN"] = f".{server_name}"
        # Important for Vercel https
        app.config["PREFERRED_URL_SCHEME"] = "https"

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    # Blueprint Registration based on Domain Configuration
    if server_name:
        # Register main website on the base domain
        app.register_blueprint(main_bp)

        # Register Admin and Auth on the 'admin' subdomain
        # Register auth first to ensure it's the primary provider for login
        app.register_blueprint(auth_bp, subdomain='admin')
        app.register_blueprint(admin_bp, subdomain='admin')
    else:
        # Local development or no subdomain setup
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp, url_prefix="/admin")

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_globals():
        return {"site_name": "NavSahaay Foundation"}

    # Initialize database connection
    try:
        from app.firebase import db
        if db:
            from app.services.seed import seed_admin_and_events
            seed_admin_and_events()
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    try:
        return User.get_by_id(user_id)
    except:
        return None
