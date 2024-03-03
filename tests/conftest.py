import pytest
from urlshortener import create_app
from urlshortener.extensions import mongo
from os import environ
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "testing",
        "MONGO_URI": environ["MONGO_URI_TEST"],
        "WTF_CSRF_ENABLED": False
    })

    # mongo needs to be mocked. Real test database is being used for now
    mongo.db.links.drop()

    with app.app_context():
        yield app

    # keeping data for troubleshooting
    # mongo.db.links.drop()


@pytest.fixture()
def client(app):
    return app.test_client()
