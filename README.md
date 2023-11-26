# urlshortener

### Requirements

- External database (tested with PostgreSQL and SQLite)

#### Environment variables

- SECRET_KEY
- DATABASE_URI
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- HOST (optional)

---

### Initial setup
1. Set upp environment variables SECRET_KEY, DATABASE_URI, GOOGLE_CLIENT_ID, and GOOGLE_CLIENT_SECRET or replace them directly in config.py
2.     from urlshortener import create_app
       from urlshortener.extensions import db
       create_app().app_context().push()
       db.create_all()


---

### Docker
- `docker build -t urlshortener .`
- `docker run -p 5000:5000 -e SECRET_KEY=1234567890abcdefghijklmnopqrstuv -e DATABASE_URI=DATABASE_URI=postgresql://user:password@127.0.0.1/urlshortener -e GOOGLE_CLIENT_ID=appid -e GOOGLE_CLIENT_SECRET=appsecret -e HOST=0.0.0.0 urlshortener`
