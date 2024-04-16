from flask import Flask
from flask_login import LoginManager
from .routes import http_reciever, http_teams_reciever, portal, api, auth_bp
from .models import db, init_db
from .services.auth_service import get_user_by_username


def create_app(config="config.Config") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    app.secret_key = app.config.get("SECRET_KEY")

    login_manager = LoginManager()
    login_manager.init_app(app=app)
    login_manager.login_view = "auth.login"

    # Database Settings
    init_db(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(portal)
    app.register_blueprint(api)
    app.register_blueprint(http_reciever)
    app.register_blueprint(http_teams_reciever)
    return app
