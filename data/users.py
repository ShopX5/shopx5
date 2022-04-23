import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    coins = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    word = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    dels = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    card_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)