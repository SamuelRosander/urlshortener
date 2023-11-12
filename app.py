from flask import Flask, render_template, url_for, redirect, request, current_app, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from wtforms import SubmitField
from wtforms.fields import URLField
from wtforms.validators import DataRequired
import random
import string
import secrets
from urllib.parse import urlencode
import requests
from os import environ

app = Flask(__name__)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)
login_manager = LoginManager(app)

@app.route("/")
def index():
    form = LinkForm()
    if current_user.is_authenticated:
        links = Link.query.filter_by(user_id=current_user.id).order_by(Link.id.desc())
    else:
        links = None

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

        if (current_user.is_authenticated):
            link = Link(long_url=form.long_url.data, short_url=short_url, user_id = current_user.id)
        else:
            link = Link(long_url=form.long_url.data, short_url=short_url)

        db.session.add(link)
        db.session.commit()

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    return redirect(url_for('info', short_url=short_url))


@app.route("/<short_url>/info")
def info(short_url):
    link = Link.query.filter_by(short_url=short_url).first()

    if link == None:
        abort(404)
    elif link.owner and link.owner != current_user:
        abort(401)

    form =LinkForm()

    return render_template("info.html", form=form, link=link)


@app.route("/<short_url>")
def redirect_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first()

    if link:
        link.no_of_clicks += 1
        db.session.commit()
        return redirect(link.long_url)
    else:
        return redirect(url_for("index"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/authorize/<provider>")
def oauth2_authorize(provider):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    session['oauth2_state'] = secrets.token_urlsafe(16)

    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    return redirect(provider_data['authorize_url'] + '?' + qs)


@app.route('/callback/<provider>')
def oauth2_callback(provider):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    if 'error' in request.args:
        return redirect(url_for('index'))

    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    if 'code' not in request.args:
        abort(401)

    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
    }, headers={'Accept': 'application/json'})
    
    if response.status_code != 200:
        abort(401)

    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })

    if response.status_code != 200:
        abort(401)

    email = provider_data['userinfo']['email'](response.json())

    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.errorhandler(401)
def error_401(error):
    return render_template("error.html", error="401 Unauthorized"), 401


@app.errorhandler(404)
def error_404(error):
    return render_template("error.html", error="404 Not found"), 404


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


class LinkForm(FlaskForm):
    long_url = URLField("Long URL", validators=[DataRequired()])
    submit = SubmitField("Shorten")


if __name__ == "__main__":
    app.run(host=environ.get("HOST", "localhost"))