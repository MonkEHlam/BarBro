from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, RadioField
from wtforms.validators import DataRequired


class TagForm(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    category = RadioField(
        "Категория тега",
        choices=[("type", "Тип"), ("base", "Основной сипрт"), ("taste", "Вкус")],
    )
    submit = SubmitField("Добавить")
