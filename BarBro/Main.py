import datetime

from flask import Flask, render_template, redirect, abort, request
from data import db_session
from forms.RegisterForm import RegisterForm
from forms.LoginForm import LoginForm
from forms.CocktailForm import CocktailForm
from data.users import User
from data.cocktails import Cocktail
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
import json
import os


app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/cocktails.db")
    db_sess = db_session.create_session()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Пароли не совпадают",
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("login.html", title="Регистрация", form=form)


@app.route("/add_cocktail", methods=["GET", "POST"])
def new_cocktail():
    form = CocktailForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if (
            db_sess.query(Cocktail)
            .filter(Cocktail.name == form.name.data.upper())
            .first()
        ):
            return render_template(
                "new_cocktail.html",
                title="Новый коктейль",
                form=form,
                message="Такой коктейль уже есть",
            )
        parts = {
            "ingridients": [ingridient for ingridient in form.ingridients.data.split()],
            "dishes": [dish for dish in form.dishes.data.split()],
        }
        cocktail = Cocktail(
            name=form.name.data,
            parts=json.dumps(parts, ensure_ascii=False),
            receipt=form.receipt.data,
            history=form.history.data if form.history.data != "" else None,
        )
        db_sess.add(cocktail)
        db_sess.commit()
        return redirect("/welcome")
    return render_template("new_cocktail.html", title="Регистрация", form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template(
            "login.html", message="Неправильный логин или пароль", form=form
        )
    return render_template("login.html", title="Авторизация", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    main()
