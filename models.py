from sqlalchemy import collate
from operator_logs import app
from config import DB_NAME
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from flask_login import UserMixin

app.config['SECRET_KEY'] = 'secret-my-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bd/{}'.format(DB_NAME)
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)
    permission = db.Column(JSON)
    settings = db.Column(JSON)
    password = db.Column(db.String(100))
    
class OperatorLogModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_event = db.Column(db.DateTime)
    event = db.Column(db.String(300))
    username_report = db.Column(db.String(25), default="-----")
    time_report = db.Column(db.String(15))
    after_event = db.Column(db.String(300), default="")
    operator = db.Column(db.String(25))

class OperatorLogModelTp(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_abon = db.Column(db.String(10))
    time_event = db.Column(db.DateTime)
    dogovor = db.Column(db.String(10), default="")
    event = db.Column(db.String(300), default="")
    phone = db.Column(db.String(15), default="")
    request = db.Column(db.String(300), default="нет")
    operator = db.Column(db.String(25))

class OperatorLogModelATC(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_event = db.Column(db.DateTime)
    event = db.Column(db.String(300))
    username_report = db.Column(db.String(25), default="-----")
    time_report = db.Column(db.String(15))
    after_event = db.Column(db.String(300), default="")
    operator = db.Column(db.String(25))

db.create_all()

