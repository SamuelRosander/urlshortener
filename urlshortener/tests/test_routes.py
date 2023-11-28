from urlshortener.models import Link, User
from flask_login import login_user
from urlshortener.extensions import db


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"<title>URL Shortener</title>" in response.data


def test_add(client, app):
    client.post("/add", data={"long_url": "https://www.url.test"})

    with app.app_context():
        assert Link.query.count() == 1
        assert len(Link.query.first().short_url) == 3
        assert Link.query.first().long_url == "https://www.url.test"


def test_info(client, app):
    client.post("/add", data={"long_url": "https://www.url.test"})
    client.post("/add", data={"long_url": "https://www.url.test"})

    with app.app_context():
        db.session.get(Link, 1).short_url = "short1"
        db.session.get(Link, 2).short_url = "add"
        db.session.commit()

    response = client.get("/short1/info")
    decoded_response_data = response.data.decode("utf-8")
    assert '<a href="/short1"' in decoded_response_data

    response = client.get("/add/info")
    decoded_response_data = response.data.decode("utf-8")
    assert '<a href="/add"' in decoded_response_data

    response = client.get("/notfound/info")
    assert response.status_code == 404


def test_short_url(client, app):
    client.post("/add", data={"long_url": "https://www.url.test"})
    client.post("/add", data={"long_url": "https://www.url.test"})

    with app.app_context():
        db.session.get(Link, 1).short_url = "short1"
        db.session.get(Link, 2).short_url = "add"
        db.session.commit()

    response = client.get("/short1")
    assert response.status_code == 303

    response = client.get("/add")
    assert response.status_code == 303

    response = client.get("/notfound")
    assert response.status_code == 404


def test_delete_link(client, app):
    client.post("/add", data={"long_url": "https://www.url.test"})

    with app.test_request_context():
        user = User(email='test@url.test')
        db.session.add(user)
        db.session.commit()
        login_user(user)

        client.post("/add", data={"long_url": "https://www.url.test"})

        db.session.get(Link, 1).short_url = "anonymous"
        db.session.get(Link, 2).short_url = "authorized"

        response = client.get("/delete/anonymous")
        assert response.status_code == 401

        response = client.get("/delete/authorized")
        assert response.status_code == 303

        response = client.get("/delete/notfound")
        assert response.status_code == 401

    response = client.get("/delete/notfound")
    assert response.status_code == 401
