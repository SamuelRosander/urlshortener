from flask import render_template, url_for, redirect, request, current_app, \
    abort, session, flash
from flask_login import current_user, logout_user, login_user, login_required
import secrets
from urllib.parse import urlencode
import requests
from .forms import LinkForm
from .models import User, Link
from .extensions import db


def create_routes(app):
    @app.route("/")
    def index():
        form = LinkForm()
        if current_user.is_authenticated:
            links = Link.query.filter_by(user_id=current_user.id) \
                .order_by(Link.id.desc())
        else:
            links = None

        return render_template("index.html", form=form, links=links)

    @app.route("/add", methods=["POST"])
    def add():
        form = LinkForm()

        if form.validate_on_submit():
            if (current_user.is_authenticated):
                link = Link(long_url=form.long_url.data,
                            user_id=current_user.id)
            else:
                link = Link(long_url=form.long_url.data)

            db.session.add(link)
            db.session.commit()

        if current_user.is_authenticated:
            return redirect(url_for('index')), 303

        return redirect(url_for('info', short_url=link.short_url)), 303

    @app.route("/<short_url>/info")
    def info(short_url):
        link = Link.query.filter_by(short_url=short_url).first()

        if link is None:
            abort(404)
        elif link.owner and link.owner != current_user:
            abort(401)

        form = LinkForm()

        return render_template("info.html", form=form, link=link)

    @app.route("/<short_url>")
    def redirect_url(short_url):
        link = Link.query.filter_by(short_url=short_url).first()

        if link:
            link.no_of_clicks += 1
            db.session.commit()
            return redirect(link.long_url), 303
        else:
            abort(404)

    @app.route("/delete/<short_url>")
    @login_required
    def delete_link(short_url):
        link = Link.query.filter_by(short_url=short_url).first()

        if not link:
            abort(401)

        if link.owner != current_user:
            abort(401)

        db.session.delete(link)
        db.session.commit()

        flash("Link has been deleted.")
        return redirect(url_for("index")), 303

    @app.route('/logout')
    def logout():
        logout_user()
        flash('You have been logged out.', "message")
        return redirect(url_for('index')), 303

    @app.route("/authorize/<provider>")
    def oauth2_authorize(provider):
        if current_user.is_authenticated:
            return redirect(url_for('index')), 303

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

        return redirect(provider_data['authorize_url'] + '?' + qs), 303

    @app.route('/callback/<provider>')
    def oauth2_callback(provider):
        if current_user.is_authenticated:
            return redirect(url_for('index')), 303

        provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            abort(404)

        if 'error' in request.args:
            for k, v in request.args.items():
                if k.startswith('error'):
                    flash(f'{k}: {v}')
            return redirect(url_for('index')), 303

        if request.args['state'] != session.get('oauth2_state') \
                or request.args['state'] is None:
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

        if response.status_code >= 300:
            abort(401)

        oauth2_token = response.json().get('access_token')
        if not oauth2_token:
            abort(401)

        response = requests.get(provider_data['userinfo']['url'], headers={
            'Authorization': 'Bearer ' + oauth2_token,
            'Accept': 'application/json',
        })

        if response.status_code >= 300:
            abort(401)

        email_extractor = provider_data['userinfo']['email']
        email = email_extractor(response.json())

        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash(f"Logged in as {user.email}", "message")
        return redirect(url_for('index')), 303

    @app.errorhandler(401)
    @app.errorhandler(404)
    def error(error):
        print(error)
        return render_template("error.html", error=error), error.code
