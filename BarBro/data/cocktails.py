import sqlalchemy
from .db_session import SqlAlchemyBase


class Cocktail(SqlAlchemyBase):
    __tablename__ = "cocktails"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    parts = sqlalchemy.Column(sqlalchemy.String)
    receipt = sqlalchemy.Column(sqlalchemy.String)
    history = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tags = sqlalchemy.Column(sqlalchemy.String, default='{tags: []}')
    with open('cocktail_plug_img.jpg', 'rb') as data:
        photo = sqlalchemy.Column(sqlalchemy.BLOB, default=open("../static/image/plug_img.png"))

    def __repr__(self):
        return f"<Cocktail> {self.id} {self.name}"
