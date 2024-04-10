from flask_pymongo import PyMongo
import string
from random import choice
import functools
from flask import session, abort

mongo = PyMongo()


def generate_short_url():
    chars = string.digits + string.ascii_letters
    short_url = ''.join(choice(chars) for i in range(3))
    link = mongo.db.links.find_one({"short_url": short_url})

    if link:
        generate_short_url()

    return short_url


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user") is None:
            abort(401)

        return view(**kwargs)

    return wrapped_view
