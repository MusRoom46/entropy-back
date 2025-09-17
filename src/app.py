import os
from flask import Flask
from routes.routes import bp
from config.config import Config
from config.db import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init DB
    db.init_app(app)

    # Register routes
    app.register_blueprint(bp)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()  # Crée les tables si elles n'existent pas

    port = int(os.getenv("PORT", 5000))

    # IMPORTANT : écouter sur 0.0.0.0 pour render
    app.run(host="0.0.0.0", port=port, debug=False)
