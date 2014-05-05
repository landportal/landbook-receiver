from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/landportal'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foo.db'
# Set debug mode so Apache can log the errors
app.config['DEBUG'] = True
db = SQLAlchemy(app)

#from app import views
