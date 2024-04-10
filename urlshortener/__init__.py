from flask import Flask
from .extensions import mongo
from .routes import create_routes


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile("config.py")

    mongo.init_app(app)

    create_routes(app)

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    return app
