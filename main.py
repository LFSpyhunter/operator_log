from flask import Blueprint, render_template
import func

main = Blueprint('main', __name__)


@main.route('/site')
def site():
    return render_template('site.html')

@main.route('/add', methods=['POST'])
def add():
    return func.add()

@main.route('/update', methods=['POST'])
def put():
    return func.put()

@main.route('/adduser', methods=['POST'])
def signup_post():
    return func.signup_post()

@main.route('/search', methods=['GET','POST'])
def search():
    return func.search()

