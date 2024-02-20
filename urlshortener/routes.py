from flask import render_template, url_for, redirect, request, current_app, \
    abort, session, flash
import secrets
from urllib.parse import urlencode
import requests
from .forms import LinkForm
from .extensions import mongo, generate_short_url, login_required
from datetime import datetime


def create_routes(app):
    @app.route("/")
    def index():
        form = LinkForm()

        if session.get("user"):
            links = mongo.db.links.find({"user": session["user"]})
        else:
            links = None

        return render_template("index.html", form=form, links=links)

    @app.route("/add", methods=["POST"])
    def add():
        form = LinkForm()

        if form.validate_on_submit():
            short_url = generate_short_url()
            link = {
                "short_url": short_url, "long_url": form.long_url.data,
                "timestamp": str(datetime.now())}

            if session.get("user"):
                link["user"] = session["user"]

            mongo.db.links.insert_one(link)

        if session.get("user"):
            return redirect(url_for('index')), 303

        return redirect(url_for('info', short_url=short_url)), 303

    @app.route("/<short_url>/info")
    def info(short_url):
        link = mongo.db.links.find_one_or_404({"short_url": short_url})

        if link.get("user") and session.get("user") != link["user"]:
            abort(401)

        form = LinkForm()

        return render_template("info.html", form=form, link=link)

    @app.route("/<short_url>")
    def redirect_url(short_url):
        link = mongo.db.links.find_one_or_404({"short_url": short_url})

        mongo.db.links.update_one(
            {"_id": link["_id"]},
            {"$set": {"nr_of_clicks": link.get("nr_of_clicks") or 0 + 1}})

        return redirect(link["long_url"]), 303

    @app.route("/delete/<short_url>")
    @login_required
    def delete_link(short_url):
        link = mongo.db.links.find_one_or_404({"short_url": short_url})

        if link.get("user") != session["user"]:
            abort(401)

        mongo.db.links.delete_one(link)

        flash("Link has been deleted.")
        return redirect(url_for("index")), 303

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index')), 303

    @app.route("/authorize/<provider>")
    def oauth2_authorize(provider):
        if session.get("user"):
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
        if session.get("user"):
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

        session.clear()
        session['user'] = email

        return redirect(url_for('index')), 303

    @app.errorhandler(401)
    def error_401(error):
        return render_template("error.html",
                               error_header="401 - Unauthorized"), 401

    @app.errorhandler(404)
    def error_404(error):
        return render_template("error.html",
                               error_header="404 - Not found"), 404
