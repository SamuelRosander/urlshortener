from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields import URLField
from wtforms.validators import DataRequired


class LinkForm(FlaskForm):
    long_url = URLField("Long URL", validators=[DataRequired()])
    submit = SubmitField("Shorten")
