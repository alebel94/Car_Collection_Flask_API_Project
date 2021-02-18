from flask import Flask
from config import Config
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import for Flask Login
from flask_login import LoginManager

from authlib.integrations.flask_client import OAuth

from flask_marshmallow import  Marshmallow

app = Flask(__name__) 

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app,db)
login_manager = LoginManager(app)
login_manager.login_view = 'signin' #specify what page to load for NON-AUTHED users. will take them back to 

oauth = OAuth(app)

ma =Marshmallow(app)


from car_collection_api import routes, models

