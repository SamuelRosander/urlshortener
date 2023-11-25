from flask_login import UserMixin
from .extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    links = db.relationship("Link", backref="owner", lazy=True)

    def get_id(self):
        return self.id


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    long_url = db.Column(db.String(), nullable=False)
    short_url = db.Column(db.String(), nullable=False)
    no_of_clicks = db.Column(db.Integer, default=0)