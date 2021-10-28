# !/usr/bin/python3
import logging
from logging.config import dictConfig
from flask import Flask
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from datetime import timedelta
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
    return User.query.get(int(user_id))


app.config["JWT_SECRET_KEY"] = "super-my-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)  
jwt = JWTManager(app)

