from flask_login import UserMixin
from .extensions import db, login_manager
import string
from random import choice


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    links = db.relationship("Link", backref="owner", lazy=True)

    def get_id(self):
        return self.id


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    long_url = db.Column(db.String(), nullable=False)
    short_url = db.Column(db.String(), nullable=False, unique=True)
    no_of_clicks = db.Column(db.Integer, default=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_url()

    def generate_short_url(self):
        chars = string.digits + string.ascii_letters

        short_url = ''.join(choice(chars) for i in range(3))
        link = self.query.filter_by(short_url=short_url).first()

        if link:
            self.generate_short_url()
        
        return short_url