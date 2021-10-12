from operator_logs import app
from config import DB_NAME
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(DB_NAME)
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000), unique=True)
    password = db.Column(db.String(100))
    
class OperatorLogModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_event = db.Column(db.String(120))
    event = db.Column(db.String(120))
    username_report = db.Column(db.String(80))
    after_event = db.Column(db.String(300))
    time_report = db.Column(db.String(120))
    status_event = db.Column(db.String(80))
    operator = db.Column(db.String(80))

db.create_all()