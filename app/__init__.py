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

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

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
