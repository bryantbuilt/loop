from flask_wtf import FlaskForm as Form
from wtforms import StringField, IntegerField, PasswordField, TextAreaField, DateField, DateTimeField, DecimalField, BooleanField, SelectField, SelectMultipleField,SubmitField,HiddenField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                               Length, EqualTo,Required)
from wtforms.fields.html5 import DateTimeField
from models import User, Account

def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')

def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    fullname = StringField(
        "Fullname",
        validators=[DataRequired()]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )

class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class AccountForm(Form):
    name = StringField('Name')
    street = StringField('Street')
    owner = SelectField('Owner')
    city = StringField('City')
    account_type = SelectField('Type', choices=[('Prospect','Prospect'),('Customer','Customer')])
    state = StringField('State')
    website = StringField('Website')
    country = StringField('Country')

class ContactForm(Form):
    account = SelectField('Account')
    owner = SelectField('Owner')
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    title = StringField('Title')
    department = StringField('Department')
    street = StringField('Street')
    city = StringField('City')
    state = StringField('State')
    country = StringField('Country')
    phone = StringField('Phone')
    email = StringField('Email')
class OpportunityForm(Form):
    account = SelectField('Account')
    name = StringField('Name')
    owner = SelectField('Owner')
    opportunity_type = SelectField('Type', choices=[('New Business','New Business'),('Upgrade','Upgrade'),('Renewal','Renewal')])
    primary_contact = SelectField('Primary Contact')
    stage = SelectField('Stage', choices=[('Qualifying','Qualifying'),('Demo','Demo'),('Pricing','Pricing'),('Closed Won','Closed Won'),('Lost','Lost')])
    close_date = DateField('Close Date')
class SubscriptionForm(Form):
    account = SelectField('Account')
    opportunity = SelectField('Opportunity')
    product = SelectField('Product')
    product_price = DecimalField('Price')
    sub_start_date = DateField('Subscription Start Date')
    quantity = IntegerField('Quantity')
    sub_end_date = DateField('Subscription End Date')
    # mrr = DecimalField('MRR',default=0)
    # arr = DecimalField('ARR',default=0)
class ProductForm(Form):
    name = StringField('Product Name')
    price = DecimalField('Price Per Unit')