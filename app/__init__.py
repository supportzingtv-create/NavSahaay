import os
from flask import Flask, redirect, url_for, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Trust Vercel's proxy for HTTPS and Host headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Ensure SECRET_KEY is never None or empty
    secret = os.getenv("SECRET_KEY") or "shivoham-fallback-secret-key-12345"
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

    # Blueprint Registration with explicit path prefix for Admin and Auth
    app.register_blueprint(auth_bp, url_prefix="/admin")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(main_bp)

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_globals():
        try:
            from app.models import Setting, Donation, Cause

            # Fetch all active causes and group them by category for Mega Menu
            all_causes = Cause.get_all(active_only=True)
            categorized_causes = {}
            for c in all_causes:
                if c.category not in categorized_causes:
                    categorized_causes[c.category] = []
                categorized_causes[c.category].append(c)

            return {
                "site_name": "NavSahaay Foundation",
                "urgent_appeal": Setting.get("urgent_appeal", {"active": False}),
                "matching": Setting.get("donation_matching", {"active": False}),
                "social": Setting.get("social_links", {}),
                "seo": Setting.get("seo_meta", {}),
                "recent_ticker": Donation.get_recent_verified(5),
                "wall_of_fame": Donation.get_recent_verified(10),
                "recent_wishes": Donation.get_recent_wishes(15),
                "transparency": Setting.get("transparency_ratios", {"programmes":"92", "admin":"5", "fundraising":"3"}),
                "mega_menu_causes": categorized_causes
            }
        except Exception as e:
            app.logger.error(f"Error in inject_globals: {e}")
            return {
                "site_name": "NavSahaay Foundation",
                "urgent_appeal": {"active": False},
                "matching": {"active": False},
                "social": {},
                "seo": {},
                "recent_ticker": [],
                "wall_of_fame": [],
                "recent_wishes": [],
                "transparency": {"programmes":"92", "admin":"5", "fundraising":"3"}
            }

    # Initialize database connection
    try:
        from app.firebase import db
        if db:
            from app.services.seed import seed_admin_and_events
            seed_admin_and_events()
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")

    @app.before_request
    def handle_admin_domain():
        if request.path.startswith('/static') or request.path.startswith('/api'):
            return

        host = request.host.lower().split(':')[0]
        # If the domain starts with 'admin' (like adminnavsahaay.vercel.app), force it to only show the admin panel
        if host.startswith('admin'):
            if not request.path.startswith('/admin'):
                from flask_login import current_user
                if current_user.is_authenticated:
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('auth.login'))

    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        from flask import render_template
        app.logger.error(f"500 Internal Server Error: {e}")
        return render_template("404.html"), 500

    return app

@login_manager.user_loader
def load_user(user_id):
    import os
    from app.models.user import User
    try:
        if not user_id: return None
        if user_id == "admin_fallback":
            env_email = os.getenv("ADMIN_EMAIL", "admin@navsahaay.org").strip().lower()
            return User(id="admin_fallback", name="NavSahaay Administrator", email=env_email, password_hash="", role="SUPER_ADMIN")
        return User.get_by_id(user_id)
    except:
        return None
