from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import db
import func

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    return func.login_post()
@auth.route('/operlog')
def operlog():
    return func.index()

@auth.route('/signup')
def signup():
    return render_template('singup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))