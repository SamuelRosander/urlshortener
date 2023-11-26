import pytest
from urlshortener import create_app, db
import os


@pytest.fixture()
def app():
    app = create_app(config_file=os.path.join("tests", "config.py"))

    with app.app_context():
        db.create_all()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()