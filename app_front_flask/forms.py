from wtforms import Form, StringField
from wtforms. validators import DataRequired


class TaskForm(Form):
    title = StringField('title', validators=[DataRequired()])