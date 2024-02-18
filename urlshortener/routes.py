from flask import render_template, url_for, redirect, request, current_app, \
    abort, session, flash
from flask_login import current_user, logout_user, login_user, login_required
import secrets
from urllib.parse import urlencode
import requests
from .forms import LinkForm
from .models import User
from .extensions import cosmos_db, db, generate_short_url
import azure.cosmos.exceptions as exceptions
from datetime import datetime


def create_routes(app):
    @app.route("/")
    def index():
        form = LinkForm()
        if current_user.is_authenticated:
            links = list(cosmos_db["links"].read_all_items())
            # links = list(cosmos_db["links"].query_items(
            #     query="SELECT * FROM r WHERE r.user_id=@user_id",
            #     parameters=[
            #         {"name": "@user_id", "value": current_user.id}
            #     ]
            # ))
        else:
            links = None

        return render_template("index.html", form=form, links=links)

    @app.route("/add", methods=["POST"])
    def add():
        form = LinkForm()

        if form.validate_on_submit():

            short_url = generate_short_url()
            link = {"id": short_url, "long_url": form.long_url.data,
                    "partitionKey": 1, "nr_of_clicks": 0,
                    "timestamp": str(datetime.now)}

            if current_user.is_authenticated:
                link["user_id"] = current_user.id

            cosmos_db["links"].create_item(body=link)

        if current_user.is_authenticated:
            return redirect(url_for('index')), 303

        return redirect(url_for('info', short_url=short_url)), 303

    @app.route("/<short_url>/info")
    def info(short_url):
        try:
            link = cosmos_db["links"].read_item(
                item=short_url, partition_key=1)
        except exceptions.CosmosResourceNotFoundError:
            abort(404)

        if link.get("user_id") and \
                link.get("user_id") != current_user.get_id():
            abort(401)

        form = LinkForm()

        return render_template("info.html", form=form, link=link)

    @app.route("/<short_url>")
    def redirect_url(short_url):
        try:
            link = cosmos_db["links"].read_item(
                item=short_url, partition_key=1)
            link["nr_of_clicks"] += 1
            cosmos_db["links"].upsert_item(body=link)
            return redirect(link["long_url"]), 303
        except exceptions.CosmosResourceNotFoundError:
            error_message = f"No URL was found for /{short_url}"
            return render_template("error.html",
                                   error_header="404 - not found",
                                   error_message=error_message), 404

    @app.route("/delete/<short_url>")
    @login_required
    def delete_link(short_url):
        try:
            link = cosmos_db["links"].read_item(
                item=short_url, partition_key=1)
        except exceptions.CosmosResourceNotFoundError:
            abort(401)

        if link.get("user_id") != current_user.get_id():
            abort(401)

        cosmos_db["links"].delete_item(item=short_url, partition_key=1)

        flash("Link has been deleted.")
        return redirect(url_for("index")), 303

    @app.route('/logout')
    def logout():
        logout_user()
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
        return redirect(url_for('index')), 303

    @app.errorhandler(401)
    def error_401(error):
        return render_template("error.html",
                               error_header="401 - Unauthorized"), 401

    @app.errorhandler(404)
    def error_404(error):
        return render_template("error.html",
                               error_header="404 - Not found"), 404
