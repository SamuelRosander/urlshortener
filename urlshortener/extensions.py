from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pymongo import PyMongo
import string
from random import choice

db = SQLAlchemy()
login_manager = LoginManager()
mongo = PyMongo()


def generate_short_url():
    chars = string.digits + string.ascii_letters

    short_url = ''.join(choice(chars) for i in range(3))
    # try:
    #     link = cosmos_db["links"].read_item(item=short_url, partition_key=1)
    # except exceptions.CosmosResourceNotFoundError:
    #     link = None

    # if link:
    #     generate_short_url()

    return short_url
