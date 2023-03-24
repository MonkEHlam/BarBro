import datetime

from flask import Flask, render_template, redirect, abort, request
from data import db_session
from data.users import User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/cocktails.db")
    db_sess = db_session.create_session()
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    return render_template("index.html")

if __name__ == '__main__':
    main()