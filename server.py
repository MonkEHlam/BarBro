from flask import Flask, render_template, redirect, abort, request
from data import db_session, my_exceptions

from forms.RegisterForm import RegisterForm
from forms.LoginForm import LoginForm
from forms.TagForm import TagForm
from forms.CocktailForm import CocktailFormBuilder
from data.users import User
from data.tags import Tag
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
from static.texts.welcome import text

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/BarBro.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


def delete_cocktail_from_tags(db_sess, id, tags):
    for tag in tags["tags"]:
        t = db_sess.query(Tag).filter(tag == Tag.name).first()
        data = json.loads(t.cocktails)
        data["cocktails"].remove(id)
        t.cocktails = json.dumps(data, ensure_ascii=False)


@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("index.html", text=text, title='Главная')


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
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/add_cocktail", methods=["GET", "POST"])
def new_cocktail():
    form = CocktailFormBuilder()
    if form.validate_on_submit():
        print("imin")
        db_sess = db_session.create_session()
        if (
            db_sess.query(Cocktail)
            .filter(Cocktail.name == form.name.data.capitalize())
            .first()
        ):
            print("error")
            return render_template(
                "new_cocktail.html",
                title="Новый коктейль",
                form=form,
                message="Такой коктейль уже есть",
            )

        parts = {
            "ingridients": [
                ingridient for ingridient in form.ingridients.data.split("\r\n")
            ],
            "dishes": [dish for dish in form.dishes.data.split("\r\n")],
        }

        cocktail = Cocktail(
            name=form.name.data.capitalize(),
            parts=json.dumps(parts, ensure_ascii=False),
            receipt=form.receipt.data,
            history=form.history.data if form.history.data != "" else None,
            tags=json.dumps(
                {
                    "tags": [
                        str(form[field].label.text)
                        for field in form.fields
                        if form[field].data
                    ]
                },
                ensure_ascii=False,
            ),
        )
        db_sess.add(cocktail)

        for field in form.fields:
            if form[field].data:
                tag = (
                    db_sess.query(Tag)
                    .filter(str(form[field].label.text) == Tag.name)
                    .first()
                )
                data = json.loads(tag.cocktails)
                data["cocktails"].append(cocktail.id)
                tag.cocktails = json.dumps(data)

        if form.photo.data:
            cocktail.photo = form.photo.data.read()

        db_sess.commit()

        return redirect("/welcome")
    return render_template("new_cocktail.html", title="Новый коктейль", form=form)


@app.route("/edit_cocktail/<int:id>", methods=["GET", "POST"])
@login_required
def edit_cocktail(id):
    if current_user.is_admin:
        form = CocktailFormBuilder()
        if request.method == "GET":
            db_sess = db_session.create_session()
            cocktail = db_sess.query(Cocktail).filter(Cocktail.id == id).first()
            if cocktail:
                form.name.data = cocktail.name
                parts = json.loads(cocktail.parts)
                form.ingridients.data = "\r\n".join(
                    json.loads(cocktail.parts)["ingridients"]
                )
                form.dishes.data = "\r\n".join(json.loads(cocktail.parts)["dishes"])
                form.history.data = (
                    cocktail.history if cocktail.history is not None else ""
                )
                form.receipt.data = cocktail.receipt

                for tag in json.loads(cocktail.tags)["tags"]:
                    for field in form.fields:
                        if str(form[field].label.text) == tag:
                            form[field].render_kw = {"checked": True}
            else:
                abort(404)

        if form.validate_on_submit():
            db_sess = db_session.create_session()
            cocktail = db_sess.query(Cocktail).filter(Cocktail.id == id).first()
            if cocktail:
                delete_cocktail_from_tags(
                    db_sess, cocktail.id, json.loads(cocktail.tags)
                )
                parts = {
                    "ingridients": [
                        ingridient for ingridient in form.ingridients.data.split("\r\n")
                    ],
                    "dishes": [dish for dish in form.dishes.data.split("\r\n")],
                }
                cocktail.name = form.name.data.capitalize()
                cocktail.parts = json.dumps(parts, ensure_ascii=False)
                cocktail.receipt = form.receipt.data
                cocktail.history = (
                    form.history.data if form.history.data != "" else None
                )
                cocktail.tags = json.dumps(
                    {
                        "tags": [
                            str(form[field].label.text)
                            for field in form.fields
                            if form[field].data
                        ]
                    },
                    ensure_ascii=False,
                )

                for field in form.fields:
                    if form[field].data:
                        tag = (
                            db_sess.query(Tag)
                            .filter(str(form[field].label.text) == Tag.name)
                            .first()
                        )
                        data = json.loads(tag.cocktails)
                        if cocktail.id not in data["cocktails"]:
                            data["cocktails"].append(cocktail.id)
                            tag.cocktails = json.dumps(data)

                if form.photo.data:
                    cocktail.photo = form.photo.data.read()
                db_sess.commit()

                return redirect("/cocktails")
        return render_template(
            "new_cocktail.html", title="Редактирование коктейля", form=form
        )


@app.route("/delete_cocktail_absolutly_super_giga_micro_pablo_sure/<int:id>")
@login_required
def delete_cocktail(id):
    if current_user.is_admin:
        db_sess = db_session.create_session()
        cocktail = db_sess.query(Cocktail).filter(Cocktail.id == id).first()
        if cocktail:
            delete_cocktail_from_tags(db_sess, cocktail.id, json.loads(cocktail.tags))
            db_sess.delete(cocktail)
            db_sess.commit()
            return redirect("/")
        else:
            abort(404)
    else:
        return redirect("/")


@app.route("/delete_photo/<int:id>")
@login_required
def delete_photo(id):
    if current_user.is_admin:
        db_sess = db_session.create_session()
        cocktail = db_sess.query(Cocktail).filter(Cocktail.id == id).first()
        if cocktail:
            cocktail.set_default_photo()
            db_sess.commit()
        return redirect("/cocktails")
    return redirect("/cocktails")


@app.route("/tag", methods=["GET", "POST"])
@login_required
def new_tag():
    form = TagForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Tag).filter(Tag.name == form.name.data.capitalize()).first():
            return render_template(
                "new_tag.html",
                title="Новый тег",
                form=form,
                message="Такой тег уже есть",
            )
        tag = Tag(name=form.name.data.capitalize(), category=form.category.data)
        db_sess.add(tag)
        db_sess.commit()
        return redirect("/tag")
    return render_template("new_tag.html", title="Новый тег", form=form)


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


def cocktails_list(tags=""):
    db_sess = db_session.create_session()
    if tags:
        cocktails_id_from_tags = []
        for tag in tags:
            cocktails_id_from_tags.append(set(tag.get_cocktails()))
        final_ids = cocktails_id_from_tags[0]
        for ids in cocktails_id_from_tags:
            final_ids = final_ids.intersection(ids)
        cocktail_list = db_sess.query(Cocktail).filter(Cocktail.id.in_(list(final_ids)))
        return cocktail_list
    else:
        cocktail_list = db_sess.query(Cocktail).all()
        return cocktail_list


@app.route("/cocktails", methods=["GET", "POST"])
def cocktail_table():
    tags = []
    if request.method == "POST":
        base_tags_id = []
        taste_tags_id = []
        type_tags_id = []
        for key, value in request.form.to_dict().items():
            if "base" in key:
                base_tags_id.append(int(value))
            if "taste" in key:
                taste_tags_id.append(int(value))
            if "type" in key:
                type_tags_id.append(int(value))
        if base_tags_id:
            tags += get_tags("base", base_tags_id)
        if taste_tags_id:
            tags += get_tags("taste", taste_tags_id)
        if type_tags_id:
            tags += get_tags("type", type_tags_id)
    return render_template(
        "cocktails_list.html",
        cocktails=cocktails_list(tags),
        tags_bases=get_tags("base"),
        tags_tastes=get_tags("taste"),
        tags_types=get_tags("type"),
        title='Список'
    )


@app.route("/cocktail/<int:id>")
def cocktail(id):
    db = db_session.create_session()
    if db.query(Cocktail).filter(Cocktail.id == id).first():
        cocktail=db.query(Cocktail).filter(Cocktail.id == id).first()
        return render_template(
            "cocktail.html",
            cocktail=cocktail,
            title=cocktail.name
        )


def get_tags(category, ids=[]):
    if category == "taste" or category == "base" or category == "type":
        db = db_session.create_session()
        if ids:
            return db.query(Tag).filter(Tag.category == category, Tag.id.in_(ids)).all()
        return db.query(Tag).filter(Tag.category == category).all()
    else:
        abort(400)


if __name__ == "__main__":
    main()
