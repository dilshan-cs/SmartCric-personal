# pyrefly: ignore [missing-import]
from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes.pages import pages_bp
    from app.routes.match_routes import match_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(match_bp, url_prefix='/api/match')

    return app
