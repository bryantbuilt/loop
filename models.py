import datetime
from peewee import *

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('loop.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    fullname = CharField()
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        
    @classmethod
    def create_user(cls, username, fullname,email, password, admin=False):
        try:
            cls.create(
                username=username,
                fullname=fullname,
                email=email,
                password=generate_password_hash(password),
                is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

class Account(Model):
    name = CharField()
    

    class Meta:
        database = DATABASE

    @classmethod
    def create_account(cls,name):
        cls.create(
            name = name)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User], safe=True)
    DATABASE.close()