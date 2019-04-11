import datetime
from peewee import *

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('loop.db', pragmas={'foreign_keys':1})

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
    owner = ForeignKeyField(model=User, null=True, backref='owner')
    created_by = ForeignKeyField(model=User, null=True, backref='creator')
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
    account = ForeignKeyField(model=Account, null=True, backref='contact')
    owner = ForeignKeyField(model=User, null=True, backref='owner')
    created_by = ForeignKeyField(model=User, null=True, backref='creator')
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
    account = ForeignKeyField(model=Account, null=True, backref='opportunity')
    name = CharField()
    owner = ForeignKeyField(model=User, null=True, backref='owner')
    opportunity_type = CharField()
    primary_contact = ForeignKeyField(model=Contact, null=True, backref='opportunity')
    mrr = DecimalField()
    arr = DecimalField()
    stage = CharField()
    close_date = DateField()
    created_by = ForeignKeyField(model=User, null=True, backref='creator')
    class Meta:
        database = DATABASE
    
    @classmethod
    def create_opportunity(cls,account,name,created_by,owner,opportunity_type,primary_contact,mrr,arr,stage,close_date):
        cls.create(
            account = account,
            name = name,
            created_by = created_by,
            owner = owner,
            opportunity_type = opportunity_type,
            primary_contact = primary_contact,
            mrr = mrr,
            arr = arr,
            stage = stage,
            close_date = close_date)

class Product(Model):
    name = CharField()
    price = DecimalField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_product(cls,name,price):
        cls.create(
            name = name,
            price = price
        )
class Subscription(Model):
    account = ForeignKeyField(model=Account, null=True, backref='subscription')
    opportunity = ForeignKeyField(model=Opportunity, null=True, backref='subscription')
    product = ForeignKeyField(model=Product, null=True, backref='subscription')
    product_price = DecimalField(default=Product.price)
    quantity = IntegerField(default=1)
    sub_start_date = DateField()
    sub_end_date = DateField()
    mrr = DecimalField()
    arr = DecimalField()
    created_by = ForeignKeyField(model=User, null=True, backref='creator')

    class Meta:
        database = DATABASE

    @classmethod
    def create_subscription(cls,account,opportunity,product,product_price,quantity,sub_start_date,sub_end_date,mrr,arr,created_by):
        cls.create(
            account = account,
            opportunity = opportunity,
            product = product,
            product_price = product_price,
            qualtity = quantity,
            sub_start_date = sub_start_date,
            sub_end_date = sub_end_date,
            mrr = mrr,
            arr = arr,
            created_by = created_by
        )

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User,Account,Contact,Opportunity,Product,Subscription], safe=True)
    DATABASE.close()