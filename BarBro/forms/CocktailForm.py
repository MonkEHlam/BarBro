from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, BooleanField, FileField
from wtforms.validators import DataRequired
import sys

sys.path.append("..")
from data import tags, db_session


class CocktailFormBase(FlaskForm):
    name = StringField("Название", validators=[DataRequired()])
    ingridients = TextAreaField(
        "Ингридиенты (Каждый на новой строке)", validators=[DataRequired()]
    )
    dishes = TextAreaField(
        "Посуда (Каждый на новой строке)", validators=[DataRequired()]
    )
    receipt = TextAreaField("Рецепт", validators=[DataRequired()])
    history = TextAreaField("История")
    photo = FileField("Фото")
    submit = SubmitField("Добавить")


def CocktailFormBuilder():
    class CocktailForm(CocktailFormBase):
        pass

    db_sess = db_session.create_session()
    for i, tag in enumerate(db_sess.query(tags.Tag).all()):
        setattr(CocktailForm, "tag_%d" % i, BooleanField(label=tag))
    form = CocktailForm()
    setattr(
        CocktailForm,
        "fields",
        [field for field in form.__dir__() if field[:3] == "tag"],
    )

    return CocktailForm()
