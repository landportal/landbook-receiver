'''
Created on 03/02/2014

@author: Herminio
'''
from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import FileHandler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/landportal'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foo.db'
db = SQLAlchemy(app)
if not app.debug:
	file_handler = FileHandler(filename='receiver_log')
	file_handler.setLevel(logging.WARNING)
	app.logger.addHandler(file_handler)

from app import views
