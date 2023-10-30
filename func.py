from datetime import datetime, timedelta
from sqlalchemy.orm.attributes import flag_modified
from flask import render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user
from sqlalchemy import or_
from operator_api import log_post_args, abort
from models import OperatorLogModel, OperatorLogModelTp, OperatorLogModelATC, User, db
from flask_jwt_extended import create_access_token
from func_for_switch import define_model
from operator_logs import app
import requests


def edit_it():
    # Функция для вывода журнала оператора IT
    if current_user.permission['edit_jur_it'] == "enable":
        kol = -int(current_user.settings['posts_kol'])
        logs = OperatorLogModel.query[kol:]
        if request.method == "POST":
            date = request.form.get('date')
            if date == "1":
                pass
            else:
                date_start = datetime.strptime("{} 00:00".format(
                    datetime.today().strftime('%Y-%m-%d')), "%Y-%m-%d %H:%M") - timedelta(days=1)
                date_end = datetime.today().strftime('%Y-%m-%d %H:%M')
                logs = OperatorLogModel.query.filter(
                    OperatorLogModel.time_event.between(date_start, date_end))
        return render_template('editit.html', logs=logs)
    else:
        return index_it()

def edit_tp():
    # Функция для вывода журнала оператора ТП
    if current_user.permission['edit_jur_tp'] == "enable":
        logs = OperatorLogModelTp.query[-10:]
        if request.method == "POST":
            date = request.form.get('date')
            if date == "1":
                logs = OperatorLogModelTp.query[-10:]
            else:
                date_start = datetime.strptime("{} 00:00".format(
                    datetime.today().strftime('%Y-%m-%d')), "%Y-%m-%d %H:%M") - timedelta(days=1)
                date_end = datetime.today().strftime('%Y-%m-%d %H:%M')
                logs = OperatorLogModelTp.query.filter(
                    OperatorLogModelTp.time_event.between(date_start, date_end))
        return render_template('edittp.html', logs=logs)
    else:
        return index_tp()

def inko_api():
     sw_info = {}
     if request.method == "POST":
        ip = request.form.get('sw')
        port = request.form.get('port')
        get_info = request.form.get('get_info')
        sw = check_ip(ip)
        if not sw:
            flash("Некорректный IP")
            return redirect("/inkoapi", 302)
        result = check_current_date(port, get_info)
        if not result[0]:
            flash(f"{result[1]}")
            return redirect("/inkoapi", 302)
        sw_info['switch'] = {"ip": sw, "port" : port}
        try:
            if get_info == "full":
                model, _, _ = define_model(sw)
                sw_info["model"] = model
                request_result_full = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}')
                request_result_mac = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/mac')
                sw_info["port_info"] = request_result_full.json()['data'][0]
                sw_info["mac"] = request_result_mac.json()['data']
                request_result_acl = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/acl')
                sw_info["acl"] = request_result_acl.json()['data']
                request_result_error = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/counters')
                sw_info["port_counters"] = request_result_error.json()['data']
                request_result_linkcount = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/linkdowncount')
                sw_info["linkcount"] = request_result_linkcount.json()['data']
            if get_info == "mac":
                request_result_mac = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/mac')
                sw_info["mac"] = request_result_mac.json()['data']
            if get_info == "log":
                request_result_log = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/log')
                sw_info["log"] = request_result_log.json()['data']
                for i in sw_info["log"]:
                    i["timestamp"] = change_date(i["timestamp"])
            if get_info == "acl":
                request_result_acl = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/acl')
                sw_info["acl"] = request_result_acl.json()['data']
            if get_info == "ddm": 
                request_result_ddm = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/ddm')
                sw_info["ddm"] = request_result_ddm.json()['data']
            if get_info == "error":
                request_result_error = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/counters')
                sw_info["port_counters"] = request_result_error.json()['data']
            if get_info == "linkcount":
                request_result_linkcount = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/linkdowncount')
                sw_info["linkcount"] = request_result_linkcount.json()['data']
            if get_info == "freeports":
                request_result_linkcount = requests.get(f'http://192.168.255.70:9999/sw/{sw}/freeports')
                sw_info["freeports"] = request_result_linkcount.json()['data']
            if get_info == "clear":
                requests.delete(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/counters')
                request_result_error = requests.get(f'http://192.168.255.70:9999/sw/{sw}/ports/{port}/counters')
                sw_info["port_counters"] = request_result_error.json()['data']
        except:
            flash("Не получилось обработать данные")
            app.logger.warning(f"Не получилось обработать запрос от {current_user.name} где IP: {ip}, port: {port} infa: '{get_info}'")
            return redirect("/inkoapi", 302)
        app.logger.info(
                f"Поступил запрос от {current_user.name} где IP: {sw}, port: {port} infa: '{get_info}' и получен ответ {sw_info}")
     return render_template('inkoapi.html', inko = sw_info)

def edit_atc():
    # Функция для вывода журнала оператора ATC
    if current_user.permission['edit_jur_atc'] == "enable":
        logs = OperatorLogModelATC.query[-10:]
        if request.method == "POST":
            date = request.form.get('date')
            if date == "1":
                logs = OperatorLogModelATC.query[-10:]
            else:
                date_start = datetime.strptime("{} 00:00".format(
                    datetime.today().strftime('%Y-%m-%d')), "%Y-%m-%d %H:%M") - timedelta(days=1)
                date_end = datetime.today().strftime('%Y-%m-%d %H:%M')
                logs = OperatorLogModelATC.query.filter(
                    OperatorLogModelATC.time_event.between(date_start, date_end))
        return render_template('editatc.html', logs=logs)
    else:
        return index_atc()

def index_it():
    # Функция для просмотра журнала операторов IT
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
    return render_template('it.html', logs=logs)


def index_tp():
    # Функция для просмотра журнала операторов ТП
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
        logs = OperatorLogModelTp.query.filter(
            OperatorLogModelTp.time_event.between(date_start, date_end))
    logs = OperatorLogModelTp.query.filter(
        OperatorLogModelTp.time_event.between(date_start, date_end))
    return render_template('tp.html', logs=logs)

def index_atc():
    # Функция для просмотра журнала операторов ATC
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
        logs = OperatorLogModelATC.query.filter(
            OperatorLogModelATC.time_event.between(date_start, date_end))
    logs = OperatorLogModelATC.query.filter(
        OperatorLogModelATC.time_event.between(date_start, date_end))
    return render_template('atc.html', logs=logs)


def add():
    if not current_user.is_authenticated:
        return abort(401)
    timestamp = int(datetime.today().strftime('%s'))
    if request.form.get('otdel') == "it":
        if current_user.permission['edit_jur_it'] == "enable":
            log_oper = OperatorLogModel(time_event=datetime.fromtimestamp(
                timestamp), event=request.form.get('event'),  operator=current_user.name)
            # now.strftime("%d-%m-%Y %H:%M")
            db.session.add(log_oper)
            db.session.commit()
            app.logger.info(
                f"Добавлена запись '{request.form.get('event')}' оператором '{current_user.name}' в отделе '{request.form.get('otdel')}'")
            return redirect("/editit", 302)
        else:
            return abort(401)
    elif request.form.get('otdel') == "tp":
        if current_user.permission['edit_jur_tp'] == "enable":
            log_oper = OperatorLogModelTp(time_event=datetime.fromtimestamp(
                timestamp), phone=request.form.get('phone'), otdel=current_user.otdel,  operator=current_user.name)
            db.session.add(log_oper)
            db.session.commit()
            app.logger.info(
                f"Добавлена запись '{request.form.get('phone')}' оператором '{current_user.name}'  в отделе '{request.form.get('otdel')}'")
            return redirect("/edittp", 302)
        else:
            return abort(401)
    elif request.form.get('otdel') == "atc":
        if current_user.permission['edit_jur_atc'] == "enable":
            log_oper = OperatorLogModelATC(time_event=datetime.fromtimestamp(
                timestamp), event=request.form.get('event'), otdel=current_user.otdel,  operator=current_user.name)
            db.session.add(log_oper)
            db.session.commit()
            app.logger.info(
                f"Добавлена запись '{request.form.get('event')}' оператором '{current_user.name}'  в отделе '{request.form.get('otdel')}'")
            return redirect("/editatc", 302)
        else:
            return abort(401)
    else:
        return abort(401)


def put():
    if not current_user.is_authenticated:
        return abort(401)
    args = log_post_args.parse_args()
    change_log = {}
    if request.form.get('otdel') == "it":
        if (current_user.permission['edit_jur_it'] == "enable" and current_user.name == args['operator']) or current_user.permission['admin_user'] == "enable":
            log = OperatorLogModel.query.filter_by(id=args['id']).first()
            if not log:
                abort(404, message="Net takogo ID")
            if args['event']:
                old_log_event = log.event
                log.event = args['event']
                if not old_log_event == log.event:
                    change_log["Событие"] = [
                        f'"{old_log_event}" ==> "{log.event}"']
            if args['username_report']:
                old_username_report = log.username_report
                log.username_report = args['username_report']
                if not old_username_report == log.username_report:
                    change_log["Кому доложил"] = [
                            f'"{old_username_report}" ==> "{log.username_report}"']
            if args['after_event']:
                old_after_event = log.after_event
                log.after_event = args['after_event']
                if not old_after_event == log.after_event:
                    change_log["Пояснение события"] = [
                        f'"{old_after_event}" ==> "{log.after_event}"']
            if args['time_report']:
                old_time_report = log.time_report
                log.time_report = args['time_report']
                if not old_time_report == log.time_report:
                    change_log["Время восстановления"] = [
                        f'"{old_time_report}" ==> "{log.time_report}"']
            app.logger.info(
                f'Изменение записи id:{log.id} "{log.event}" {change_log} оператором "{current_user.name}"')
            db.session.commit()
            return redirect("/editit", 302)
    elif request.form.get('otdel') == "tp":
        if (current_user.permission['edit_jur_tp'] == "enable" and current_user.name == args['operator']) or current_user.permission['admin_user'] == "enable":  # переделать получение данных
            dogovor = request.form.get('dogovor')
            phone = request.form.get('phone')
            zayavka = request.form.get('request')
            log = OperatorLogModelTp.query.filter_by(id=args['id']).first()
            if not log:
                abort(404, message="Net takogo ID")
            if args['event']:
                old_event = log.event
                log.event = args['event']
                if not old_event == log.event:
                    change_log["Суть проблемы"] = [
                        f'"{old_event}" ==> "{log.event}"']
            if dogovor:
                old_dogovor = log.dogovor
                log.dogovor = dogovor
                if not old_dogovor == log.dogovor:
                    change_log["Договор"] = [
                        f'"{old_dogovor}" ==> "{log.dogovor}"']
            if phone:
                old_phone = log.phone
                log.phone = phone
                if not old_phone == log.phone:
                    change_log["Телефон"] = [f'"{old_phone}" ==> "{log.phone}"']
            if zayavka:
                old_zayavka = log.request  # поменять название
                log.request = zayavka
                if not old_zayavka == log.request:
                    change_log["Заявка"] = [f'"{old_zayavka}" ==> "{log.request}"']
            app.logger.info(
                f'Изменение записи id:{log.id} "{log.phone}" {change_log} оператором "{current_user.name}"')
            db.session.commit()
            return redirect("/edittp", 302)
    else:
        flash("Нельзя редактировать записи другого оператора")
        return redirect("/edittp", 302)

def delete():
    if not current_user.is_authenticated:
        return abort(401)
    id = request.form.get('id')
    otdel = request.form.get('otdel')
    if otdel == "it":
        log = OperatorLogModel.query.filter_by(id=id).first()
        app.logger.warning(
            f"Удалена запись id:'{log.id}', суть события: '{log.event}', пояснение события: '{log.after_event}' оператором '{current_user.name}' в отделе '{otdel}'")
        db.session.delete(log)
        db.session.commit()
        return redirect("editit", 302)
    if otdel == "tp":
        log = OperatorLogModelTp.query.filter_by(id=id).first()
        app.logger.warning(
            f"Удалена запись id:'{log.id}', договор: '{log.dogovor}', суть проблемы: '{log.event}', телефон: '{log.phone}'  оператором '{current_user.name}' в отделе '{log.otdel}'")
        db.session.delete(log)
        db.session.commit()
        return redirect("/edittp", 302)
    if otdel == "atc":
        if current_user.permission['edit_jur_atc'] == "enable" or current_user.permission['admin_user'] == "enable":
            log = OperatorLogModelTp.query.filter_by(id=id).first()
            app.logger.warning(
                f"Удалена запись id:'{log.id}', суть события: '{log.event}', пояснение события: '{log.after_event}' оператором '{current_user.name}' в отделе '{otdel}'")
            db.session.delete(log)
            db.session.commit()
        return redirect("/edittp", 302)


def delete_user():
    if not current_user.is_authenticated:
        return abort(401)
    id = request.form.get('id')
    user = User.query.filter_by(id=id).first()
    if not user:
        abort(404, message="Net takogo Usera")
    app.logger.warning(
        f'Удаление пользователя "{user.name}" оператором "{current_user.name}"')
    db.session.delete(user)
    db.session.commit()
    return redirect("/admin", 302)


def signup_post():
    name = request.form.get('name')
    password = request.form.get('password')
    permission = {"search": "disable", "create_news": "disable", "inko_api": "disable", "prosm_jur_it": "enable", "prosm_jur_tp": "disable",
                  "prosm_jur_atc": "disable", "edit_jur_it": "disable", "edit_jur_tp": "disable", "edit_jur_atc": "disable",
                  "prosm_switch": "disable", "set_port": "disable", "set_switch": "disable", "del_entry": "disable",
                  "edit_entry": "disable", "admin_user": "disable"}
    settings = {"posts_kol": "6"}
    user = User.query.filter_by(name=name).first()
    if user:
        flash('Такой пользователь уже существует')
        return redirect(url_for('auth.signup'))
    new_user = User(name=name, permission=permission,  settings=settings, password=generate_password_hash(
        password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    app.logger.warning(
        f'Добавился пользователь с фамилией "{name}"')
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
    return redirect("/")


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
        if request.form.get('otdel_report') == "IT":
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
            date_logs = OperatorLogModel.query.filter(OperatorLogModel.time_event.between(date_start, date_end), or_(
                OperatorLogModel.event.like(f'%{event}%'), OperatorLogModel.after_event.like(f'%{event}%')))
            return render_template('search.html', logs=date_logs)
        if request.form.get('otdel_report') == "TP":
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
            date_logs = OperatorLogModelTp.query.filter(OperatorLogModelTp.time_event.between(date_start, date_end), or_(
                OperatorLogModelTp.dogovor.like(f'%{event}%'), OperatorLogModelTp.phone.like(f'%{event}%')))
            return render_template('search.html', logs_tp=date_logs)
    return render_template('search.html')


def admin():
    if not current_user.is_authenticated:
        return abort(401)
    else:
        users = ""
        if current_user.permission['admin_user'] == "enable" or current_user.name == 'Брянский':
            users = User.query.all()
            if request.method == "POST":
                id = request.form.get('id')
                user = User.query.filter_by(id=id).first()
                if not user:
                    abort(404, message="Net takogo Usera")
                else:
                    for key, value in request.form.items():
                        if key == "id":
                            pass
                        elif user.permission[key] == value:
                            pass
                        else:
                            app.logger.info(
                                f'Изменение пользователя "{user.name}"  разрешение "{key}: {user.permission[key]} ==> {value}" оператором "{current_user.name}"')
                            user.permission[key] = value
                            flag_modified(user, "permission")
                            db.session.commit()
                users = User.query.all()
        else:
            return render_template('index.html')
        return render_template('admin.html', users=users)
    
def get_user_settings():
    result = current_user.settings
    return result

def set_user_settings():
    kolvo = request.form.get('kolvo')
    name = current_user.name
    user = User.query.filter_by(name=name).first()
    print(user)
    if not user:
        abort(404, message="Net takogo Usera")
    else:
        user.settings['posts_kol'] = kolvo
        flag_modified(user, "settings")
        db.session.commit()
    return redirect("/editit")

def check_current_date(port, get_info):
    get_info_abon = ["full", "log", "clear", "error"]
    get_info_magistr = ["log", "ddm", "clear", "error"]
    get_info_mont = ["freeports"]
    get_info_list = get_info_abon + get_info_magistr + get_info_mont
    if get_info not in get_info_list:
        return False, "Нет такого запроса"
    if port:
        if  0 < int(port) < 29:
            if get_info in get_info_abon and 0 < int(port) < 25:
                return True, "Все верно"
            elif get_info in get_info_magistr and 24 < int(port) < 29:
                return True, "Все верно"
            else:
                return False, "Запрос неккоректен"
        else:
            return False, "Неккоректный порт"
    else:
        if get_info in get_info_mont:
            return True, "Все верно"
        else:
            return False, "Введите порт"

def check_ip(ip):
    ip_net_list = ["47", "49", "57", "58", "59", "60", "90"]
    if ip.count('.') == 3:
        a, b, net, ip = ip.split(".")
        if net in ip_net_list:
            if 1 < int(ip) < 250:
                return f'192.168.{net}.{ip}'
            else:
                return False
        else:
            return False
    elif ip.count('.') == 1:
        net, ip = ip.split(".")
        if net in ip_net_list:
            if 1 < int(ip) < 250:
                return f'192.168.{net}.{ip}'
            else:
                return False
        else:
            return False
    else:
        return False

def change_date(date):
    date = date.split("T")
    time, _ = date[1].split(".")
    time = time.split(":")
    time[0] = str(int(time[0]) + 3)
    if int(time[0]) > 23:
        time[0] = str(int(time[0]) - 24)
    date = f'{date[0]} {":".join(time)}'
    return date

def logs_app():
    with open('operators.log', 'r') as h:
            date = h.read()
    return render_template('logs.html', date=date)