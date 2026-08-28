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
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "local-dev-secret")
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
        return {"site_name": "Shivoham Foundation"}

    # Initialize Firestore and seed if necessary
    from app.services.seed import seed_admin_and_events
    seed_admin_and_events()

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.get_by_id(user_id)
