from os import environ
from urlshortener import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host=environ.get("HOST", "localhost"))
