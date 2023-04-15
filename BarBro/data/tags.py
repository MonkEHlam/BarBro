import sqlalchemy
from .db_session import SqlAlchemyBase
import json


class Tag(SqlAlchemyBase):
    __tablename__ = "tags"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    cocktails = sqlalchemy.Column(
        sqlalchemy.String, default=json.dumps({"cocktails": []})
    )

    def __repr__(self):
        return f"{self.name}"

    def get_cocktails(self):
        return json.loads(self.cocktails)["cocktails"]
