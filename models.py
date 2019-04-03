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
    owner = ForeignKeyField(model=User,backref='owner')
    created_by = ForeignKeyField(model=User,backref='creator')
    account_type = CharField()
    street = CharField()
    city = CharField()
    state = CharField()
    country = CharField()
    website = CharField()
    mrr = DecimalField()
    arr = DecimalField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_account(cls,name,owner,created_by,account_type,street,city,state,country,website,mrr,arr):
        cls.create(
            name = name,
            owner = owner,
            created_by = created_by,
            account_type = account_type,
            street = street,
            city = city,
            state = state,
            country = country,
            website = website,
            mrr = mrr,
            arr = arr)

class Contact(Model):
    account = ForeignKeyField(model=Account,backref='contact')
    owner = ForeignKeyField(model=User,backref='owner')
    created_by = ForeignKeyField(model=User,backref='creator')
    first_name = CharField()
    last_name = CharField()
    title = CharField()
    department = CharField()
    street = CharField()
    city = CharField()
    state = CharField()
    country = CharField()
    phone = CharField()
    email = CharField()
    class Meta:
        database = DATABASE

    @classmethod
    def create_contact(cls,account,owner,created_by,first_name,last_name,title,department,street,city,state,country,phone,email):
        cls.create(
            account = account,
            owner = owner,
            created_by = created_by,
            first_name = first_name,
            last_name = last_name,
            title = title,
            department = department,
            street = street,
            city = city,
            state = state,
            country = country,
            phone = phone,
            email = email)

class Opportunity(Model):
    account = ForeignKeyField(model=Account,backref='opportunity')
    name = CharField()
    owner = ForeignKeyField(model=User,backref='owner')
    opportunity_type = CharField()
    primary_contact = ForeignKeyField(model=Contact,backref='opportunity')
    mrr = DecimalField()
    arr = DecimalField()
    stage = CharField()
    created_by = ForeignKeyField(model=User,backref='creator')
    class Meta:
        database = DATABASE
    
    @classmethod
    def create_opportunity(cls,account,name,created_by,owner,opportunity_type,primary_contact,mrr,arr,stage):
        cls.create(
            account = account,
            name = name,
            created_by = created_by,
            owner = owner,
            opportunity_type = opportunity_type,
            primary_contact = primary_contact,
            mrr = mrr,
            arr = arr,
            stage = stage)
    
class Subscription(Model):
    account = ForeignKeyField(model=Account,backref='subscription')
    opportunity = ForeignKeyField(model=Opportunity,backref='opportunity')
    product = CharField()
    discount = DecimalField()
    sub_start_date = DateField()
    sub_end_date = DateField()
    mrr = DecimalField()
    arr = DecimalField()
    created_by = ForeignKeyField(model=User,backref='creator')

    class Meta:
        database = DATABASE
    
    

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User,Account,Contact,Opportunity,Subscription], safe=True)
    DATABASE.close()