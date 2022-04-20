import sqlalchemy
from .db_session import SqlAlchemyBase


class Item(SqlAlchemyBase):
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, index=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    seller = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cart = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    fast = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    free = sqlalchemy.Column(sqlalchemy.String, nullable=True)