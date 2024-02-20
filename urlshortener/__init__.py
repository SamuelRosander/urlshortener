from flask import Flask
from .extensions import db, login_manager, mongo
from .routes import create_routes


def create_app(config_file="config.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    db.init_app(app)
    login_manager.init_app(app)
    mongo.init_app(app)

    create_routes(app)

    return app
