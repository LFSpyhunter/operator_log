from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import db
import manage_switch 
import func


auth = Blueprint('auth', __name__)


@auth.route('/', methods=['GET','POST'])
def index():
    if not current_user.is_authenticated:
        return render_template('enter.html')
    else:
        return render_template('index.html')

@auth.route('/inkoapi', methods=['GET','POST'])
@login_required
def inko_api():
    return func.inko_api()

@auth.route('/it', methods=['GET','POST'])
@login_required
def it():
    return func.index_it()

@auth.route('/tp', methods=['GET','POST'])
@login_required
def tp():
    return func.index_tp()

@auth.route('/atc', methods=['GET','POST'])
@login_required
def atc():
    return func.index_atc()

@auth.route('/editit', methods=['GET','POST'])
@login_required
def editit():
    return func.edit_it()

@auth.route('/edittp', methods=['GET','POST'])
@login_required
def edittp():
    return func.edit_tp()

@auth.route('/editatc', methods=['GET','POST'])
@login_required
def editatc():
    return func.edit_atc()

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    return func.login_post()

@auth.route("/loginapi", methods=["POST"])
def login_api():
    return func.login_api()

@auth.route('/signup')
def signup():
    return render_template('singup.html')

@auth.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    return func.admin()
    

@auth.route('/delete', methods=['POST'])
def delete():
    return func.delete() 

@auth.route('/userdelete', methods=['POST'])
def userdelete():
    return func.delete_user() 

@auth.route('/getsettings', methods=['GET'])
def getsettings():
    return func.get_user_settings()

@auth.route('/setsettings', methods=['POST'])
def setsettings():
    return func.set_user_settings()

@auth.route('/portinfo', methods=['POST'])
def portinfo():
    return manage_switch.port_info()

@auth.route('/setport', methods=['POST'])
def setport():
    return manage_switch.set_port()

@auth.route('/switch', methods=['GET','POST'])
@login_required
def switch():
    return manage_switch.switch_view()

@auth.route('/setswitch', methods=['GET','POST'])
def setswitch():
    return manage_switch.set_switch()

@auth.route('/getconfig', methods=['POST'])
def get_config():
    return manage_switch.get_config()

@auth.route('/tmpconfig', methods=['POST'])
def tmp_config():
    return manage_switch.tmp_config()

@auth.route('/cfgdownload', methods=['POST'])
def cfg_download():
    return manage_switch.upload_config()

@auth.route('/saveswitch', methods=['GET'])
def saveswitch():
    return manage_switch.save_switch()

@auth.route('/refresh', methods=['GET','POST'])
@login_required
def refresh():
    return manage_switch.switch_refresh()

@auth.route('/switchlog', methods=['GET'])
def switch_log():
    return manage_switch.switch_log()

@auth.route('/logs', methods=['GET'])
@login_required
def logs_app():
    return func.logs_app()


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
