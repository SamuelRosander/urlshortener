from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import random
import string

app = Flask(__name__)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)


@app.route("/")
def index():
    form = LinkForm()
    links = Link.query.order_by(Link.link_id.desc()).all()
    return render_template("index.html", form=form, links=links)


@app.route("/add", methods=["POST"])
def add():
    form = LinkForm()
    if form.validate_on_submit():
        chars = string.digits + string.ascii_letters
        
        while (True):
            short_url = ''.join(random.choice(chars) for i in range(3))
            link_exists = Link.query.filter_by(short_url=short_url).first()

            if not link_exists:
                break

        link = Link(long_url=form.long_url.data, short_url=short_url)
        db.session.add(link)
        db.session.commit()
    return redirect(url_for('index'))


@app.route("/<short_url>")
def redirect_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first()

    if link:
        return redirect(link.long_url)
    else:
        return redirect(url_for("index"))


class Link(db.Model):
    link_id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(), nullable=False)
    short_url = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"Link('{self.link_id}', '{self.short_url}')"


class LinkForm(FlaskForm):
    long_url = StringField("Long URL", validators=[DataRequired()])
    submit = SubmitField("Shorten")


if __name__ == "__main__":
    app.run(host='0.0.0.0')