from flask import session
from urlshortener.extensions import mongo


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"<title>URL Shortener</title>" in response.data


def test_add(client):
    client.post("/add", data={"long_url": "https://www.url.test"})

    assert mongo.db.links.estimated_document_count() == 1
    assert len(mongo.db.links.find_one()["short_url"]) == 3
    assert mongo.db.links.find_one()["long_url"] == "https://www.url.test"


def test_short_url_and_info(client):
    client.post("/add", data={"long_url": "https://www.url1.test"})
    client.post("/add", data={"long_url": "https://www.url2.test"})

    link1 = mongo.db.links.find_one({"long_url": "https://www.url1.test"})
    link2 = mongo.db.links.find_one({"long_url": "https://www.url2.test"})

    mongo.db.links.update_one(
        {"_id": link1["_id"]},
        {"$set": {"short_url": "add"}})
    mongo.db.links.update_one(
        {"_id": link2["_id"]},
        {"$set": {"short_url": "short1"}})

    response = client.get("/short1")
    assert response.status_code == 303

    response = client.get("/add")
    assert response.status_code == 303

    response = client.get("/notfound")
    assert response.status_code == 404

    response = client.get("/short1/info")
    decoded_response_data = response.data.decode("utf-8")
    assert '<a href="/short1"' in decoded_response_data

    response = client.get("/add/info")
    decoded_response_data = response.data.decode("utf-8")
    assert '<a href="/add"' in decoded_response_data

    response = client.get("/notfound/info")
    assert response.status_code == 404


def test_delete_link(client, app):
    client.post("/add", data={"long_url": "https://www.url1.test"})

    with app.test_request_context():
        session["user"] = "user@test.test"

        assert session["user"] == "user@test.test"

        # this does not work. session["user"] is accessible here but is None
        # in the actual route.
        client.post("/add", data={"long_url": "https://www.url2.test"})

        link1 = mongo.db.links.find_one(
            {"long_url": "https://www.url1.test"})
        link2 = mongo.db.links.find_one(
            {"long_url": "https://www.url2.test"})

        mongo.db.links.update_one(
            {"_id": link1["_id"]},
            {"$set": {"short_url": "anonymous"}})
        mongo.db.links.update_one(
            {"_id": link2["_id"]},
            {"$set": {"short_url": "authorized"}})

        response = client.get("/delete/anonymous")
        assert response.status_code == 401

        # will fail since i cant figure out how to get access
        # to session["user"] in the route
        response = client.get("/delete/authorized")
        assert response.status_code == 303

        response = client.get("/delete/notfound")
        assert response.status_code == 401

        response = client.get("/delete/notfound")
        assert response.status_code == 401
