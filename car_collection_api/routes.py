
import jwt
from car_collection_api import app, db, oauth
from flask import render_template, request, redirect, url_for, flash, session, jsonify

from car_collection_api.forms import UserLoginForm
from car_collection_api.models import User, check_password_hash,Car,  car_schema, cars_schema

#imports for flask login
from flask_login import login_user, logout_user, current_user, login_required

import os
from car_collection_api.helpers import get_jwt, token_required, verify_owner


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = UserLoginForm()

    try:
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            print(email, password)

            user = User(email, password = password)

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('signin'))
    except:
        raise Exception('Invalid For Data: Please Check your form')

    return render_template('signup.html', form=form)

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    form = UserLoginForm()

    try:
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            print(email, password)

            logged_user = User.query.filter(User.email == email).first()
            if logged_user and check_password_hash(logged_user.password, password):
                login_user(logged_user)
                flash('You were successfully logged in: Via Email/Password', 'auth-success')
                return redirect(url_for('home'))
            else:
                flash('Your Email/Password is incorrect', 'auth-failed')
                return redirect(url_for('signin'))

    except:
        raise Exception('Invalid For Data: Please Check your form')

    return render_template('signin.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    if session:
        for key in list(session.keys()):
            session.pop(key)
    return redirect(url_for('home'))

@app.route('/profile', methods = ['GET'])
@login_required
def profile():
    jwt = get_jwt(current_user)
    print(current_user.token)
    return render_template('profile.html', jwt = jwt)

# CREATE Car ENDPOINT
@app.route('/cars', methods=['POST'])
@token_required
def create_car(current_user_token):
    print(current_user_token)
    name = request.json['name']
    price = request.json['price']
    model = request.json['model']
    user_id = current_user_token.token

    car = Car(name,price,model, user_id = user_id)

    db.session.add(car)
    db.session.commit()

    response = car_schema.dump(car)
    return jsonify(response)

# RETRIEVE ALL Cars ENDPOINT
@app.route('/cars', methods = ['GET'])
@token_required
def get_cars(current_user_token):
    owner, current_user_token = verify_owner(current_user_token)
    cars = Car.query.filter_by(user_id = owner.user_id).all()
    response = car_schema.dump(cars)
    return jsonify(response)


# RETIREVE ONE Car ENDPOINT
@app.route('/cars/<id>', methods= ['GET'])
@token_required
def get_car(current_user_token, id):
    owner, current_user_token = verify_owner(current_user_token)
    car = Car.query.get(id)
    response = car_schema.dump(car)
    return jsonify(response)



    #Google OAUTH Routes and Config info
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)


@app.route('/google-auth')
def google_auth():
    google= oauth.create_client('google')
    redirect_uri = url_for('authorize', _external = True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    response = google.get('userinfo')
    user_info = response.json()
    user= oauth.google.userinfo()
    session['profile'] = user_info

    user = User.query.filter_by(email = user_info['email']).first()
    if user:
        user.first_name = user_info['given_name']
        user.last_name = user_info['family_name']
        user.email = user_info['email']
        user.g_auth_verify = user_info['verified_email']

        db.session.add(user)
        db.session.commit()
        login_user(user)
        session.permanent = True
        return redirect(url_for('home'))

    else:
        g_first_name = user_info['given_name']
        g_last_name = user_info['family_name']
        g_email = user_info['email']
        g_verified = user_info['verified_email']

        user = User(
            first_name = g_first_name,
            last_name = g_last_name,
            email = g_email,
            g_auth_verify = g_verified,
        )

        db.session.add(user)
        db.session.commit()
        session.permanent = True
        login_user(user)
        return redirect(url_for('home'))

    print(user_info)
    return redirect(url_for('home'))
