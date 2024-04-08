# urlshortener

A web app that shortens long URLs  with a randomized, 3-character code. Can be used both anonymous or authenticated with oauth2, using Google as provider.

### Requirements

- External database (tested with PostgreSQL and SQLite)

#### Environment variables needed

- SECRET_KEY
- DATABASE_URI
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- HOST (optional)

---

### Initial setup
1.      git clone https://github.com/SamuelRosander/urlshortener.git
        cd urlshortener
        copy .env.sample .env
        python -m venv .venv
        .venv\Scripts\activate
        pip install -r .\requirements.txt
2. Set up environment variables in .env
3. Have your database ready
4.      from urlshortener import create_app
        from urlshortener.extensions import db
        from dotenv import load_dotenv
        load_dotenv()
        create_app().app_context().push()
        db.create_all()


---

### Running locally (Windows)
1.      .venv\Scripts\activate
        flask run
2. Accessible on http://localhost:5000

---

### Docker
1.      docker build . -t urlshortener
2.      docker run -p 8000:8000 -e SECRET_KEY=1234567890abcdefghijklmnopqrstuv -e DATABASE_URI=postgresql://user:password@127.0.0.1/urlshortener -e GOOGLE_CLIENT_ID=appid -e GOOGLE_CLIENT_SECRET=appsecret urlshortener
3. Accessible on http://localhost:8000