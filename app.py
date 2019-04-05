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

# Account CRUD
@app.route('/account', methods=['GET'])
@app.route('/account/', methods=['GET'])
@app.route('/account/r', methods=['GET'])
@app.route('/account/<accountid>', methods=['GET'])
@app.route('/account/<accountid>/r', methods=['GET'])
def account(accountid=None):
    form = forms.AccountForm()
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    accounts = models.Account.select()
    if accountid != None:
        account = models.Account.select().where(accountid == models.Account.id).get()
        return render_template('account-detail.html', account=account)
    return render_template('account.html', form=form, accounts=accounts)

@app.route('/account/create', methods=['GET','POST'])
@login_required
def create_account(accountid=None):
    form = forms.AccountForm()
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
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
    return render_template('create.html', form=form)

@app.route('/account/<accountid>/edit', methods=['GET','POST'])
@login_required
def edit_account(accountid):
    form = forms.AccountForm()
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    record = models.Account.select().where(accountid == models.Account.id).dicts().get()
    if form.validate_on_submit():
        flash("Account updated!", 'success')
        edited_account = models.Account.update(
            name = form.name.data,
            owner = form.owner.data,
            account_type = form.account_type.data,
            street = form.street.data,
            city = form.city.data,
            state = form.state.data,
            country = form.country.data,
            website = form.website.data,
            mrr = form.mrr.data,
            arr = form.arr.data
        ).where(accountid == models.Account.id)
        edited_account.execute()
        return redirect(url_for('account', accountid=accountid))
    return render_template('edit.html', form=form, record=record)

# Contact CRUD
# @app.route('/contact', methods=['GET'])
# @app.route('/contact/', methods=['GET'])
# @app.route('/contact/<contactid>', methods=['GET'])
# @app.route('/contact/<contactid>/r', methods=['GET'])
# def contact(contactid=None):


@app.route('/contact/create', methods=['GET','POST'])
@login_required
def create_contact():
    form = forms.ContactForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    if form.validate_on_submit():
        flash("Contact created!", 'success')
        models.Contact.create_contact(
            account = form.account.data,
            owner = form.owner.data,
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
    return render_template('create.html', form=form)

@app.route('/contact/<contactid>/edit', methods=['GET','POST'])
@login_required
def contact():
    form = forms.ContactForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    if form.validate_on_submit():
        flash("Contact created!", 'success')
        edited_contact = models.Contact.update(
            account = form.account.data,
            owner = form.owner.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            title = form.title.data,
            department = form.department.data,
            street = form.street.data,
            city = form.city.data,
            state = form.state.data,
            country = form.country.data,
            email = form.email.data,
            phone = form.phone.data
        )
        edited_contact.execute()
        # Add path back to contact detail
    return render_template('edit.html', form=form)

@app.route('/opportunity', methods=['GET','POST'])
@login_required
def opportunity():
    form = forms.OpportunityForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    form.primary_contact.choices = [(str(contact.id), (contact.first_name + ' ' + contact.last_name)) for contact in models.Contact.select()]
    if form.validate_on_submit():
        flash("Opportunity created", 'success')
        models.Opportunity.create_opportunity(
            account = form.account.data,
            name = form.name.data,
            created_by = g.user._get_current_object(),
            owner = form.owner.data,
            opportunity_type = form.opportunity_type.data,
            primary_contact = form.primary_contact.data,
            mrr = form.mrr.data,
            arr = form.arr.data,
            stage = form.stage.data
        )
    return render_template('opportunity.html', form=form)

@app.route('/subscription', methods=['GET','POST'])
@login_required
def subscription():
    form = forms.SubscriptionForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.opportunity.choices = [(str(opportunity.id), opportunity.name) for opportunity in models.Opportunity.select()]
    form.product.choices = [(str(product.id), product.name) for product in models.Product.select()]
    if form.validate_on_submit():
        flash("Subscription created",'success')
        models.Subscription.create_subscription(
            account = form.account.data,
            opportunity = form.opportunity.data,
            product = form.product.data,
            list_price = form.list_price.data,
            discount = form.discount.data,
            sale_price = form.sale_price.data,
            sub_start_date = form.sub_start_date.data,
            sub_end_date = form.sub_end_date.data,
            mrr = form.mrr.data,
            arr = form.arr.data,
            created_by = g.user._get_current_object()
        )
    return render_template('subscription.html', form=form)

@app.route('/subscription/<subscriptionid>/edit', methods=['GET','POST'])
@login_required
def edit_subscription(subscriptionid):
    form = forms.SubscriptionForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.opportunity.choices = [(str(opportunity.id), opportunity.name) for opportunity in models.Opportunity.select()]
    form.product.choices = [(str(product.id), product.name) for product in models.Product.select()]
    record = models.Subscription.select().where(subscriptionid == models.Subscription.id).dicts().get()
    if form.validate_on_submit():
        flash("Subscription update",'success')
        edit_subscription = models.Subscription.update(
            account = form.account.data,
            opportunity = form.opportunity.data,
            product = form.product.data,
            list_price = form.list_price.data,
            discount = form.discount.data,
            sale_price = form.sale_price.data,
            sub_start_date = form.sub_start_date.data,
            sub_end_date = form.sub_end_date.data,
            mrr = form.mrr.data,
            arr = form.arr.data,
        ).where(subscriptionid == models.Subscription.id)
        edit_subscription.execute()
    return render_template('edit.html', form=form, record=record)

@app.route('/product', methods=['GET','POST'])
@login_required
def product():
    form = forms.ProductForm()
    if form.validate_on_submit():
        flash('Product Created','success')
        models.Product.create_product(
            name = form.name.data,
            price = form.price.data
        )
    return render_template('product.html', form=form)


if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, port=PORT)
