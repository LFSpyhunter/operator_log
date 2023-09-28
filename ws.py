from time import sleep
from operator_logs import app
from flask_socketio import SocketIO, send, emit
from models import OperatorLogModel, OperatorLogModelTp
from datetime import datetime

socketio = SocketIO(app)

@socketio.on('connect', namespace='/it')
def connect():
    sleep(0.7)
    date_start = datetime.strptime("{} 00:00:00".format(
        datetime.today().strftime('%Y-%m-%d')), "%Y-%m-%d %H:%M:%S")
    date_end = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    logs_it = OperatorLogModel.query.filter(
        OperatorLogModel.time_event.between(date_start, date_end))
    log_all = {}
    for log in logs_it:
        log_all[log.id] = {'time_event': log.time_event.strftime(
            '%Y-%m-%d %H:%M'),  'event': log.event, 'username_report': log.username_report, 'time_report': log.time_report, 'after_event': log.after_event, 'operator': log.operator}
    emit('for it', log_all, broadcast=True)
    
@socketio.on('my event', namespace='/it')
def handle_my_custom_event(json):
    emit('for_edit_it', broadcast=True)

@socketio.on('connect', namespace='/tp')
def connect():
    sleep(0.7)
    date_start = datetime.strptime("{} 00:00:00".format(
    datetime.today().strftime('%Y-%m-%d')), "%Y-%m-%d %H:%M:%S")
    date_end = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    logs_tp = OperatorLogModelTp.query.filter(
      OperatorLogModelTp.time_event.between(date_start, date_end))
    log_all = {}
    for log in logs_tp:
        log_all[log.id] = {'time_event': log.time_event.strftime(
            '%Y-%m-%d %H:%M'), 'dogovor': log.dogovor, 'event': log.event, 'phone': log.phone, 'request': log.request, 'operator': log.operator}
    emit('for tp', log_all, broadcast=True)


    
