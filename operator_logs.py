# !/usr/bin/python3
import logging
from logging.config import dictConfig
from flask import Flask
from flask_login import LoginManager
from config import LOGGING

dictConfig(LOGGING)


app = Flask(__name__)
app.logger = logging.getLogger('operators')
app.logger.info("Operators started")

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)


from main import main as main_blueprint
app.register_blueprint(main_blueprint)

import operator_api

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from models import User

@login_manager.user_loader
def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))