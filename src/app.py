import os
from flask import Flask
from flask_cors import CORS
from routes.routes import bp
from config.config import Config
from config.db import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Keep cookie settings consistent with our Config defaults
    app.config["SESSION_COOKIE_SAMESITE"] = Config.COOKIE_SAMESITE
    app.config["SESSION_COOKIE_SECURE"] = Config.COOKIE_SECURE

    db.init_app(app)
    app.register_blueprint(bp)

    CORS(
        app,
        resources={r"/*": {"origins": Config.CORS_ALLOWED_ORIGINS}},
        supports_credentials=True,
    )

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()

    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
