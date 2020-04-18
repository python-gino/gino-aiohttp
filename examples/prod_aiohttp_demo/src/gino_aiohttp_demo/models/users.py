from . import db


class User(db.Model):
    __tablename__ = "prod_aiohttp_demo_users"

    id = db.Column(db.BigInteger(), primary_key=True)
    nickname = db.Column(db.Unicode(), default="unnamed")
