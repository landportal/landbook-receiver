from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy
from config import *


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foo.db'
#app.config['SQLALCHEMY_DATABASE_URI'] ="mysql+mysqlconnector://"+MYSQL_USER+":"+MYSQL_PASSWORD+"@"+MYSQL_URL+":"+MYSQL_PORT+"/"+MYSQL_DATABASE
# Set debug mode so Apache can log the errors
app.config['DEBUG'] = True
db = SQLAlchemy(app)

from app import views

