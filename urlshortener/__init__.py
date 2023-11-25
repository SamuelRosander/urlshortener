from flask import Flask
from .extensions import db, login_manager
from .routes import short

def create_app(config_file="config.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(short)

    return app