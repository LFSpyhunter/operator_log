import datetime
import getpass
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user
from models import User
from flask import render_template, redirect
from operator_api import log_post_args, abort
from models import OperatorLogModel, db


def index():
    logs = OperatorLogModel.query.all()[-10:]
    return render_template('operlog.html', logs=logs)
def index_all():
    logs = OperatorLogModel.query.all()[-20:]
    return render_template('index.html', logs=logs)    

def add():
    now = datetime.datetime.now()
    args = log_post_args.parse_args()
    log_oper = OperatorLogModel(time_event=now.strftime("%d-%m-%Y %H:%M"), event=args['event'], username_report=args['username_report'],
                                after_event=args['after_event'], time_report=args['time_report'], status_event=args['status_event'], operator=current_user.name)
    db.session.add(log_oper)
    db.session.commit()
    return redirect("/operlog", 302)

def put():
    args = log_post_args.parse_args()
    log = OperatorLogModel.query.filter_by(id=args['id']).first()
    if not log:
        abort(404, message="Net takogo ID")
    if args['event']:
        log.event = args['event']
    if args['username_report']:
        log.username_report = args['username_report']
    if args['after_event']:
        log.after_event = args['after_event']
    if args['time_report']:
        log.time_report = args['time_report']
    if args['status_event']:
        log.status_event = args['status_event']
    db.session.commit()
    return redirect("/operlog", 302)

def signup_post():
    name = request.form.get('name')
    password = request.form.get('password')
    user = User.query.filter_by(name=name).first() # if this returns a user, then the email already exists in database
    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Такой пользователь уже существует')
        return redirect(url_for('auth.signup'))
    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(name=name, password=generate_password_hash(password, method='sha256'))
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login'))


def login_post():
    name = request.form.get('name')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(name=name).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Неправильный логин или пароль')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('auth.operlog'))

