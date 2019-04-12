from flask import Flask, g
from flask import render_template, flash, redirect, url_for, request, jsonify, Markup
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
from peewee import fn, JOIN

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
@login_required
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
@app.route('/account/<accountid>/', methods=['GET'])
@app.route('/account/<accountid>/r', methods=['GET'])
def account(accountid=None):
    accounts = models.Account.select()
    title = 'Accounts'
    acct_w_opps = models.Account.select(models.Account.id, models.Account.name, fn.COUNT(models.Opportunity.id).alias('open_opps')).join(models.Opportunity, JOIN.LEFT_OUTER, on=((models.Account.id == models.Opportunity.account_id) & (models.Opportunity.stage != 'Closed Won') & (models.Opportunity.stage != 'Lost'))).group_by(models.Account.id, models.Account.name)
    if accountid != None:
        title = 'Account Details'
        account = models.Account.select().where(accountid == models.Account.id).get()
        opportunities = models.Opportunity.select().where(accountid == models.Opportunity.account_id)
        return render_template('account-detail.html', account=account, user=g.user._get_current_object(), opportunities=opportunities, title=title)
    print(acct_w_opps)
    return render_template('account.html', accounts=accounts, title=title, acct_w_opps=acct_w_opps)

@app.route('/account/create', methods=['GET','POST'])
@login_required
def create_account(accountid=None):
    form = forms.AccountForm()
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    title = 'Create Account'
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
            mrr = 0,
            arr = 0
        )
        return redirect ('account')
    return render_template('create.html', form=form, title=title)

@app.route('/account/<accountid>/edit', methods=['GET','POST'])
@login_required
def edit_account(accountid):
    form = forms.AccountForm()
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    record = models.Account.select().where(accountid == models.Account.id).dicts().get()
    title = 'Edit Account'
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
    return render_template('edit.html', form=form, record=record, title=title)

@app.route('/account/<accountid>/delete', methods=['GET','POST'])
@login_required
def delete_account(accountid):
    user = g.user._get_current_object()
    account = models.Account.select().where(models.Account.id == accountid).get()
    if ((accountid != None) and (user.id == account.owner.id)):
        delete_account = models.Account.delete().where(models.Account.id == accountid)
        delete_account.delete_instance(recursive=True, delete_nullable=False)
        return redirect(url_for('account'))
    return render_template('account.html')

# Contact CRUD
@app.route('/contact', methods=['GET'])
@app.route('/contact/', methods=['GET'])
@app.route('/contact/r', methods=['GET'])
@app.route('/contact/<contactid>', methods=['GET'])
@app.route('/contact/<contactid>/', methods=['GET'])
@app.route('/contact/<contactid>/r', methods=['GET'])
def contact(contactid=None):
    contacts = models.Contact.select()
    title = 'Contacts'
    if contactid != None:
        contact = models.Contact.select().where(models.Contact.id == contactid).get()
        title = 'Contact Details'
        return render_template('contact-detail.html', contact=contact, user=g.user._get_current_object(), title=title)
    return render_template('contact.html', contacts=contacts, title=title)


@app.route('/contact/create', methods=['GET','POST'])
@login_required
def create_contact():
    form = forms.ContactForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    title = 'Create Contact'
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
        return redirect ('contact')
    return render_template('create.html', form=form, title=title)

@app.route('/contact/<contactid>/edit', methods=['GET','POST'])
@login_required
def edit_contact(contactid):
    form = forms.ContactForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    record = models.Contact.select().where(contactid == models.Contact.id).dicts().get()
    title = 'Edit Contact'
    if form.validate_on_submit():
        flash("Contact edited", 'success')
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
        return redirect(url_for('contact'))
    return render_template('edit.html', form=form, record=record, title=title)

@app.route('/contact/<contactid>/delete', methods=['GET','POST'])
@login_required
def delete_contact(contactid):
    user = g.user._get_current_object()
    contact = models.Contact.select().where(models.Contact.id == contactid).get()
    if ((contactid != None) and (user.id == contact.owner.id)):
        delete_contact = models.Contact.select().where(models.Contact.id == contactid).get()
        delete_contact.delete_instance(recursive=True, delete_nullable=False)
        return redirect(url_for('contact'))
    return render_template('contact.html')

# Opportunity CRUD
@app.route('/opportunity', methods=['GET'])
@app.route('/opportunity/', methods=['GET'])
@app.route('/opportunity/r', methods=['GET'])
@app.route('/opportunity/<opportunityid>', methods=['GET'])
@app.route('/opportunity/<opportunityid>/', methods=['GET'])
@app.route('/opportunity/<opportunityid>/r', methods=['GET'])
def opportunity(opportunityid=None):
    opportunities = models.Opportunity.select()
    opp_stage_data = models.Opportunity.select(models.Opportunity.stage,fn.SUM(models.Opportunity.mrr).alias('mrr_in_stage')).group_by(models.Opportunity.stage)
    title = 'Opportunities'
    if opportunityid != None:
        opportunity = models.Opportunity.select().where(models.Opportunity.id == opportunityid).get()
        subscriptions = models.Subscription.select().where(models.Subscription.opportunity_id == opportunityid)
        prod_mrr = models.Subscription.select(models.Subscription.product, fn.SUM(models.Subscription.mrr).alias('mrr')).where(models.Subscription.opportunity_id == opportunityid).group_by(models.Subscription.product)
        print(prod_mrr)
        title = 'Opportunity Details'
        return render_template('opportunity-detail.html', opportunity=opportunity, user=g.user._get_current_object(), subscriptions=subscriptions, prod_mrr=prod_mrr, title=title)
    return render_template('opportunity.html', opportunities=opportunities, title=title, opp_stage_data=opp_stage_data)

@app.route('/opportunity/create', methods=['GET','POST'])
@app.route('/opportunity/create/<accountid>', methods=['GET','POST'])
@login_required
def create_opportunity(accountid=None):
    form = forms.OpportunityForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    form.primary_contact.choices = [(str(contact.id), (contact.first_name + ' ' + contact.last_name)) for contact in models.Contact.select()]
    title = 'Create Opportunity'
    if form.validate_on_submit():
        flash("Opportunity created", 'success')
        models.Opportunity.create_opportunity(
            account = form.account.data,
            name = form.name.data,
            created_by = g.user._get_current_object(),
            owner = form.owner.data,
            opportunity_type = form.opportunity_type.data,
            primary_contact = form.primary_contact.data,
            mrr = 0,
            arr = 0,
            stage = form.stage.data,
            close_date = form.close_date.data
        )
        if accountid != None:
            return redirect(url_for('account', accountid=accountid))
        return redirect('opportunity')
    return render_template('create.html', form=form, title=title, accountid=accountid)

@app.route('/opportunity/<opportunityid>/edit', methods=['GET','POST'])
@login_required
def edit_opportunity(opportunityid):
    form = forms.OpportunityForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.owner.choices = [(str(user.id), user.fullname) for user in models.User.select()]
    form.primary_contact.choices = [(str(contact.id), (contact.first_name + ' ' + contact.last_name)) for contact in models.Contact.select()]
    record = models.Opportunity.select().where(opportunityid == models.Opportunity.id).dicts().get()
    title = 'Edit Opportunity'
    if form.validate_on_submit():
        flash("Opportunity updated", 'success')
        edited_opp = models.Opportunity.update(
            account = form.account.data,
            name = form.name.data,
            owner = form.owner.data,
            opportunity_type = form.opportunity_type.data,
            primary_contact = form.primary_contact.data,
            stage = form.stage.data,
            close_date = form.close_date.data
        ).where(opportunityid == models.Opportunity.id)
        edited_opp.execute()
        return redirect('opportunity')
    return render_template('edit.html', form=form, record=record, title=title)

@app.route('/opportunity/<opportunityid>/delete', methods=['GET','POST'])
@login_required
def delete_opportunity(opportunityid):
    user = g.user._get_current_object()
    opportunity = models.Opportunity.select().where(models.Opportunity.id == opportunityid).get()
    if ((opportunityid != None) and (user.id == opportunity.owner.id)):
        delete_opportunity = models.Opportunity.select().where(models.Opportunity.id == opportunityid).get()
        delete_opportunity.delete_instance(recursive=True, delete_nullable=False)
        return redirect(url_for('opportunity'))
    return render_template('opportunity.html')

# Subscription CRUD
@app.route('/subscription', methods=['GET'])
@app.route('/subscription/', methods=['GET'])
@app.route('/subscription/r', methods=['GET'])
@app.route('/subscription/<subscriptionid>', methods=['GET'])
@app.route('/subscription/<subscriptionid>/', methods=['GET'])
@app.route('/subscription/<subscriptionid>/r', methods=['GET'])
def subscription(subscriptionid=None):
    subscriptions = models.Subscription.select()
    title = 'Subscriptions'
    if subscriptionid != None:
        subscription = models.Subscription.select().where(models.Subscription.id == subscriptionid).get()
        title = 'Subscription Details'
        return render_template('subscription-detail.html', subscription=subscription, user=g.user._get_current_object(), title=title)
    return render_template('subscription.html', subscriptions=subscriptions, title=title)

@app.route('/subscription/create', methods=['GET','POST'])
@login_required
def create_subscription():
    form = forms.SubscriptionForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.opportunity.choices = [(str(opportunity.id), opportunity.name) for opportunity in models.Opportunity.select()]
    form.product.choices = [(str(product.id), product.name) for product in models.Product.select()]
    products = models.Product.select()
    title = 'Create Subscription'
    if form.validate_on_submit():
        flash("Subscription created",'success')
        sub_create = models.Subscription.create(
            account = form.account.data,
            opportunity = form.opportunity.data,
            product = form.product.data,
            product_price = form.product_price.data,
            quantity = form.quantity.data,
            sub_start_date = form.sub_start_date.data,
            sub_end_date = form.sub_end_date.data,
            mrr = form.product_price.data * form.quantity.data,
            arr = form.product_price.data * form.quantity.data * 12,
            created_by = g.user._get_current_object()
        )
        sub_create.save()
        subscriptionid = sub_create.id
        sub_account_id = models.Subscription.select(models.Subscription.account_id).where(subscriptionid == models.Subscription.id)
        new_account_mrr = models.Subscription.select(fn.SUM(models.Subscription.mrr)).where(models.Subscription.account_id == sub_account_id)
        new_account_arr = models.Subscription.select(fn.SUM(models.Subscription.arr)).where(models.Subscription.account_id == sub_account_id)
        models.Account.update(mrr = new_account_mrr,arr = new_account_arr).where(models.Account.id == sub_account_id).execute()
        sub_opp_id = models.Subscription.select(models.Subscription.opportunity_id).where(subscriptionid == models.Subscription.id)
        new_opp_mrr = models.Subscription.select(fn.SUM(models.Subscription.mrr)).where(models.Subscription.opportunity_id == sub_opp_id)
        new_opp_arr = models.Subscription.select(fn.SUM(models.Subscription.arr)).where(models.Subscription.opportunity_id == sub_opp_id)
        models.Opportunity.update(mrr = new_opp_mrr, arr = new_opp_arr).where(models.Opportunity.id == sub_opp_id).execute()
        return redirect('subscription')
    return render_template('create.html', form=form, products=products, title=title)

@app.route('/subscription/<subscriptionid>/edit', methods=['GET','POST'])
@login_required
def edit_subscription(subscriptionid):
    form = forms.SubscriptionForm()
    form.account.choices = [(str(account.id), account.name) for account in models.Account.select()]
    form.opportunity.choices = [(str(opportunity.id), opportunity.name) for opportunity in models.Opportunity.select()]
    form.product.choices = [(str(product.id), product.name) for product in models.Product.select()]
    record = models.Subscription.select().where(subscriptionid == models.Subscription.id).dicts().get()
    title = 'Edit Subscription'
    products = models.Product.select()
    if form.validate_on_submit():
        flash("Subscription update",'success')
        edit_subscription = models.Subscription.update(
            account = form.account.data,
            opportunity = form.opportunity.data,
            product = form.product.data,
            product_price = form.product_price.data,
            quantity = form.quantity.data,
            sub_start_date = form.sub_start_date.data,
            sub_end_date = form.sub_end_date.data,
            mrr = form.product_price.data * form.quantity.data,
            arr = form.product_price.data * form.quantity.data * 12,
        ).where(subscriptionid == models.Subscription.id)
        edit_subscription.execute()
        sub_account_id = models.Subscription.select(models.Subscription.account_id).where(subscriptionid == models.Subscription.id)
        new_account_mrr = models.Subscription.select(fn.SUM(models.Subscription.mrr)).where(models.Subscription.account_id == sub_account_id)
        new_account_arr = models.Subscription.select(fn.SUM(models.Subscription.arr)).where(models.Subscription.account_id == sub_account_id)
        models.Account.update(mrr = new_account_mrr,arr = new_account_arr).where(models.Account.id == sub_account_id).execute()
        sub_opp_id = models.Subscription.select(models.Subscription.opportunity_id).where(subscriptionid == models.Subscription.id)
        new_opp_mrr = models.Subscription.select(fn.SUM(models.Subscription.mrr)).where(models.Subscription.opportunity_id == sub_opp_id)
        new_opp_arr = models.Subscription.select(fn.SUM(models.Subscription.arr)).where(models.Subscription.opportunity_id == sub_opp_id)
        models.Opportunity.update(mrr = new_opp_mrr, arr = new_opp_arr).where(models.Opportunity.id == sub_opp_id).execute()
        return redirect('subscription')
    return render_template('edit.html', form=form, record=record, title=title, products=products)

@app.route('/subscription/<subscriptionid>/delete', methods=['GET','POST'])
@login_required
def delete_subscription(subscriptionid):
    user = g.user._get_current_object()
    subscription = models.Subscription.select().where(models.Subscription.id == subscriptionid).get()
    if subscriptionid != None:
        # subscription has no owner, create logic
        delete_subscription = models.Subscription.select().where(models.Subscription.id == subscriptionid).get()
        delete_subscription.delete_instance(recursive=True, delete_nullable=False)
        return redirect(url_for('subscription'))
    return render_template('subscription.html')

# Product CRUD
@app.route('/product', methods=['GET','POST'])
@app.route('/product/', methods=['GET','POST'])
@app.route('/product/r', methods=['GET','POST'])
@app.route('/product/<productid>', methods=['GET','POST'])
@app.route('/product/<productid>/', methods=['GET','POST'])
@app.route('/product/<productid>/r', methods=['GET','POST'])
@login_required
def product(productid=None):
    form = forms.ProductForm()
    products = models.Product.select()
    title = 'Products'
    if form.validate_on_submit():
        flash('Product Created','success')
        models.Product.create_product(
            name = form.name.data,
            price = form.price.data
        )
        return redirect('product')
    return render_template('product.html', form=form, products=products, title=title)

@app.route('/product/<productid>/edit', methods=['GET','POST'])
@login_required
def edit_product(productid):
    form = forms.ProductForm()
    record = models.Product.select().where(models.Product.id == productid).dicts().get()
    title = 'Edit Product'
    if form.validate_on_submit():
        flash('Product updated','success')
        edit_product = models.Product.update(
            name = form.name.data,
            price = form.price.data
        ).where(productid == models.Product.id)
        edit_product.execute()
        return redirect('product')
    return render_template('edit.html', form=form, record=record, title=title)

@app.route('/product/<productid>/delete', methods=['GET','POST'])
@login_required
def delete_product(productid):
    user = g.user._get_current_object()
    product = models.Product.select().where(models.Product.id == productid).get()
    if (productid != None): 
        # add admin user field/logic to require admin status before delete
        delete_product = product
        delete_product.delete_instance(recursive=True, delete_nullable=False)
        return redirect(url_for('product'))
    return render_template('product.html')

# User CRUD
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    title = 'Profile'
    return render_template('profile.html', title=title)

if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, port=PORT)
