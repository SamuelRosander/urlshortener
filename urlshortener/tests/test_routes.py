from urlshortener.models import Link

def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"<title>URL Shortener</title>" in response.data

def test_add(client, app):
    response = client.post("/add", data={"long_url": "https://www.url.com"})

    with app.app_context():
        assert Link.query.count() == 1
        assert len(Link.query.first().short_url) == 3
        assert Link.query.first().long_url == "https://www.url.com"


def test_info(client):
    client.post("/add", data={"long_url": "https://www.url.com", "short_url": "asd"})
    client.post("/add", data={"long_url": "https://www.url.com", "short_url": "add"})

    response = client.get(f"/asd/info")
    decoded_response_data = response.data.decode("utf-8")
    assert f'<a href="/asd"' in decoded_response_data

    response = client.get(f"/add/info")
    decoded_response_data = response.data.decode("utf-8")
    assert f'<a href="/add"' in decoded_response_data

    response = client.get(f"/asdf/info")
    assert response.status_code == 404


def test_short_url(client):
    client.post("/add", data={"long_url": "https://www.url.com", "short_url": "asd"})
    client.post("/add", data={"long_url": "https://www.url.com", "short_url": "add"})

    response = client.get(f"/asd")
    assert response.status_code == 302

    response = client.get(f"/add")
    assert response.status_code == 302

    response = client.get(f"/asdf")
    assert response.status_code == 404
