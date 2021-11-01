from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user
from models import User
from flask import render_template, redirect, jsonify
from operator_api import log_post_args, abort
from models import OperatorLogModel, db
from flask_jwt_extended import create_access_token


def index():
    logs = OperatorLogModel.query.all()[-10:]
    if not current_user.is_authenticated:
        return index_all()
    if request.method == "POST":
        date = request.form.get('date')
        if date == "1":
            logs = OperatorLogModel.query.all()[-10:]
        else:
            date_start = datetime.strptime("{} 00:00".format(
                datetime.today().strftime('%Y-%m-%d')), "%Y-%m-%d %H:%M") - timedelta(days=1)
            date_end = datetime.today().strftime('%Y-%m-%d %H:%M')
            logs = OperatorLogModel.query.filter(
                OperatorLogModel.time_event.between(date_start, date_end))

    return render_template('operlog.html', logs=logs)


def index_all():
    date_start = datetime.strptime("{} 00:00".format(
        datetime.today().strftime('%Y-%m-%d')), "%Y-%m-%d %H:%M")
    date_end = datetime.today().strftime('%Y-%m-%d %H:%M')
    if request.method == "POST":
        date = request.form.get('date')
        if date == "1":
            date_start = datetime.strptime("{} 00:00".format(
                datetime.today().strftime('%Y-%m-%d')), "%Y-%m-%d %H:%M")
            date_end = datetime.today().strftime('%Y-%m-%d %H:%M')
        else:
            date_start = datetime.strptime("{} 00:00".format(
                datetime.today().strftime('%Y-%m-%d')), "%Y-%m-%d %H:%M") - timedelta(days=3)
            date_end = datetime.today().strftime('%Y-%m-%d %H:%M')
        logs = OperatorLogModel.query.filter(
            OperatorLogModel.time_event.between(date_start, date_end))
    logs = OperatorLogModel.query.filter(
        OperatorLogModel.time_event.between(date_start, date_end))
    return render_template('index.html', logs=logs)


def add():
    if not current_user.is_authenticated:
        return abort(401)
    timestamp = int(datetime.today().strftime('%s'))
    args = log_post_args.parse_args()
    log_oper = OperatorLogModel(time_event=datetime.fromtimestamp(
        timestamp), event=args['event'], username_report=args['username_report'], time_report=args['time_report'], after_event=args['after_event'],  operator=current_user.name)
    # now.strftime("%d-%m-%Y %H:%M")
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


def search():
    if request.method == "POST":
        if request.form.get('date1') and request.form.get('date2'):
            date_start = datetime.strptime("{} 00:00".format(
                request.form.get('date1')), "%Y-%m-%d %H:%M")
            date_end = datetime.strptime("{} 23:59".format(
                request.form.get('date2')), "%Y-%m-%d %H:%M")
        else:
            date_start = ""
            date_end = ""
        if not request.form.get('date1') and not request.form.get('date2') and request.form.get('event'):
            date_start = ""
            date_end = datetime.today().strftime('%Y-%m-%d %H:%M')
        event = request.form.get('event')
        date_logs = OperatorLogModel.query.filter(OperatorLogModel.time_event.between(
            date_start, date_end), OperatorLogModel.event.like("%{}%".format(event)))
        return render_template('search.html', logs=date_logs)
    return render_template('search.html')
