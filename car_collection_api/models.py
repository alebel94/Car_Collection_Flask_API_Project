from enum import unique
from car_collection_api import app, db, login_manager, ma
import uuid
from datetime import datetime

#Adding Flask Security for passwords
from werkzeug.security import generate_password_hash, check_password_hash

#import for Secrets Module (Given by Python)
import secrets

#import for login manage
from flask_login import UserMixin 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key = True)
    first_name = db.Column(db.String(150), nullable = True, default = '')
    last_name = db.Column(db.String(150), nullable = True, default = '')
    email = db.Column(db.String(150), nullable = False)
    password = db.Column(db.String, nullable = True, default = '')
    g_auth_verify = db.Column(db.Boolean, default = False)
    token = db.Column(db.String, default = '', unique=True)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    car = db.relationship('Car', backref = 'owner', lazy = True)


    def __init__(self, email, first_name = '', last_name = '', id = '', password = '', g_auth_verify = False):
        self.id = self.set_id()
        self.first_name = first_name
        self.last_name = last_name
        self.password = self.set_password(password)
        self.email = email
        self.token = self.set_token(24)
        self.g_auth_verify = g_auth_verify

    def set_token(self,length):
        return secrets.token_hex(length)
        

    def set_id(self):
        return str(uuid.uuid4())

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash

    def __repr__(self):
        return f'User {self.email} has been added to the database'

class Car(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))
    price = db.Column(db.Integer)
    model = db.Column(db.String(150))
    user_id = db.Column(db.String, db.ForeignKey('user.token'), nullable = False)

    def __init__(self, name, price, model, user_id):
        self.name = name
        self.price = price
        self.model = model
        self.user_id = user_id

    def __repr__(self):
        return f'The following Car has been added: {self.name} which belongs tp {self.user_id}'

    def to_dict(self):
        return{
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "model": self.model
        }

# Creation of API Schema via the Marshmallow Object
class CarSchema(ma.Schema):
    class Meta:
        fields = ['id', 'name', 'price', 'model']

car_schema = CarSchema()
cars_schema = CarSchema(many = True)