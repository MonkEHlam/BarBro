from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class TagForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    submit = SubmitField("Добавить")
