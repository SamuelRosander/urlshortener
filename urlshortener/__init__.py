from flask import Flask
from .extensions import mongo
from .routes import create_routes


def create_app(config_file="config.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    mongo.init_app(app)

    create_routes(app)

    return app
