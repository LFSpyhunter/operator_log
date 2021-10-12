from flask import Blueprint, render_template
from flask_login import login_required, current_user
import func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return func.index_all()

