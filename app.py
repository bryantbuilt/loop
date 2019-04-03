from flask import Flask, g
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
from peewee import fn

import models
import forms
import json
from datetime import datetime

DEBUG = True
PORT = 8000

app = Flask(__name__)
app.secret_key = 'x'

login_manager = LoginManager()
# sets up our login for the app
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Successful signup!", 'success')
        models.User.create_user(
            username=form.username.data,
            fullname=form.fullname.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email doesn't exist")
        else:
            if check_password_hash(user.password, form.password.data):
                # creates session
                login_user(user)
                flash("You've been logged in", "success")
                user_id = user.id

                return redirect(url_for('index'))
            else:
                flash("your email or password doesn't match", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out", 'success')
    return redirect(url_for('index'))

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = forms.AccountForm()
    if form.validate_on_submit():
        flash("Account created!", 'success')
        models.Account.create_account(
            name = form.name.data,
            owner = g.user._get_current_object(),
            created_by = g.user._get_current_object(),
            account_type = form.account_type.data,
            street = form.street.data,
            city = form.city.data,
            state = form.state.data,
            country = form.country.data,
            website = form.website.data,
            mrr = form.mrr.data,
            arr = form.arr.data
        )
    return render_template('account.html', form=form)

@app.route('/contact', methods=['GET','POST'])
@login_required
def contact():
    form = forms.ContactForm()
    accounts = models.Account.select()
    users = models.User.select()
    if form.validate_on_submit():
        flash("Contact created!", 'success')
        models.Contact.create_contact(
            account = request.form.get('account'),
            owner = request.form.get('owner'),
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            title = form.title.data,
            department = form.department.data,
            street = form.street.data,
            city = form.city.data,
            state = form.state.data,
            country = form.country.data,
            created_by = g.user._get_current_object(),
            email = form.email.data,
            phone = form.phone.data
        )
    return render_template('contact.html', form=form, accounts=accounts, users=users)

@app.route('/opportunity', methods=['GET','POST'])
@login_required
def opportunity():
    form = forms.OpportunityForm()
    # form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    # form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    accounts = models.Account.select()
    users = models.User.select()
    contacts = models.Contact.select()
    # print(form.account.data)
    print(g.user._get_current_object())
    if form.validate_on_submit():
        # print(form.account.data)
        # print(form.owner.data)
        flash("Opportunity created!", 'success')
        models.Opportunity.create_opportunity(
            account = request.form.get('account'),
            name = form.name.data,
            created_by = g.user._get_current_object(),
            owner = request.form.get('owner'),
            opportunity_type = form.opportunity_type.data,
            primary_contact = request.form.get('contact'),
            mrr = form.mrr.data,
            arr = form.arr.data,
            stage = form.stage.data
        )
    return render_template('opportunity.html', form=form, accounts=accounts, users=users, contacts=contacts)

if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, port=PORT)
