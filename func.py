import datetime
from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user
from models import User
from flask import render_template, redirect, jsonify
from operator_api import log_post_args, abort
from models import OperatorLogModel, db
from flask_jwt_extended import create_access_token


def index():
    logs = OperatorLogModel.query[-20:]
    # logs = OperatorLogModel.query.all()[-10:]
    if not current_user.is_authenticated:
        return index_all()
    return render_template('operlog.html', logs=logs)


def index_all():
    logs = OperatorLogModel.query[-40:]
    # logs = OperatorLogModel.query.all()[-20:]
    return render_template('index.html', logs=logs)


def add():
    if not current_user.is_authenticated:
        return abort(401)
    now = datetime.datetime.now()
    args = log_post_args.parse_args()
    log_oper = OperatorLogModel(time_event=now.strftime("%d-%m-%Y %H:%M"), event=args['event'], username_report=args['username_report'],
                                after_event=args['after_event'], time_report=args['time_report'], status_event=args['status_event'], operator=current_user.name)
    db.session.add(log_oper)
    db.session.commit()
    return redirect("/operlog", 302)


def put():
    if not current_user.is_authenticated:
        return abort(401)
    args = log_post_args.parse_args()
    if not args['operator'] == current_user.name:
        flash("Нельзя редактировать записи другого оператора")
        return redirect("/operlog", 302)
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
    user = User.query.filter_by(name=name).first()
    if user:
        flash('Такой пользователь уже существует')
        return redirect(url_for('auth.signup'))
    new_user = User(name=name, password=generate_password_hash(
        password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login'))


def login_post():
    name = request.form.get('name')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(name=name).first()
    if not user or not check_password_hash(user.password, password):
        flash('Неправильный логин или пароль')
        return redirect(url_for('auth.login')) 
    login_user(user, remember=remember)
    
    return redirect(url_for('auth.operlog'))

def login_api():
    name = request.json.get("username", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(name=name).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify(msg="You shall not pass"), 401
    access_token = create_access_token(identity=name)
    return jsonify(access_token=access_token)
