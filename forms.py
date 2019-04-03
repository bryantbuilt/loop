from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, TextAreaField, DateField, DateTimeField, DecimalField, BooleanField, SelectField, SelectMultipleField,SubmitField,HiddenField
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
    account_type = StringField('Type')
    street = StringField('Street')
    city = StringField('City')
    state = StringField('State')
    country = StringField('Country')
    website = StringField('Website')
    mrr = DecimalField('MRR')
    arr = DecimalField('ARR')
    # Need Owner and Created By
class ContactForm(Form):
    # account = ForeignKeyField(model=Account,backref='contact')
    # owner = ForeignKeyField(model=User,backref='owner')
    # created_by = ForeignKeyField(model=User,backref='creator')
    # opportunity = ForeignKeyField(model=Opportunity,backref='contact')
    # account = HiddenField('Hidden')
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
    # account = HiddenField('Hidden')
    name = StringField('Name')
    # owner = HiddenField('Hidden')
    opportunity_type = StringField('Type')
    primary_contact = StringField('Primary Contact')
    mrr = DecimalField('MRR')
    arr = DecimalField('ARR')
    stage = StringField('Stage')
