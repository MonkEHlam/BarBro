import sys
import os.path
import sqlalchemy
from .db_session import SqlAlchemyBase, create_session
import json

sys.path.append("..")


class Cocktail(SqlAlchemyBase):
    __tablename__ = "cocktails"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    parts = sqlalchemy.Column(
        sqlalchemy.String
    )  # json like {"ingridients": [str, str...], "dishes": [str, str...]}
    receipt = sqlalchemy.Column(sqlalchemy.String)
    history = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tags = sqlalchemy.Column(sqlalchemy.String, default="{tags: []}")
    with open(
        "./static/image/plug_img.png",
        "rb",
    ) as data:
        photo = sqlalchemy.Column(sqlalchemy.BLOB, default=data.read())

    def __repr__(self):
        return f"<Cocktail> {self.id} {self.name}"

    def get_photo(self):
        with open(f"./static/image/{self.id}.png", "wb") as file:
            file.write(self.photo)
            return str(self.id) + ".png"

    def clear_photo(self):
        if os.path.isfile(f"./static/image/{self.id}.png"):
            os.remove(f"./static/image/{self.id}.png")

    def set_default_photo(self):
        with open(
            "./static/image/plug_img.png",
            "rb",
        ) as data:
            self.photo = data.read()
            print(1)

    def get_ingridients(self):
        data = json.loads(self.parts)
        return [ingridient for ingridient in data["ingridients"]]

    def get_dishes(self):
        data = json.loads(self.parts)
        return [ingridient for ingridient in data["dishes"]]
