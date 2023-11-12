# urlshortener

A simple project to shorten user URLs

---

### Requirements

- External database (tested with PostgreSQL)

#### Environment variables

- SECRET_KEY
- DATABASE_URI
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- HOST (optional)

---

### Initial setup
1. Set upp environment variables SECRET_KEY and DATABASE_URI
2.     from app import app
       from app import db
       app.app_context().push()
       db.create_all()


---

### Docker
- `docker build -t urlshortener .`
- `docker run -p 5000:5000 -e SECRET_KEY=1234567890abcdefghijklmnopqrstuv -e DATABASE_URI=DATABASE_URI=postgresql://user:password@127.0.0.1/urlshortener -e HOST=0.0.0.0 urlshortener`
