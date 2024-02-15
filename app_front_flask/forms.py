from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class GroceriesForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
