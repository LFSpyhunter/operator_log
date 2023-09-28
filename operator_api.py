from datetime import datetime
from operator_logs import app
from models import OperatorLogModel, db
from flask_restful import reqparse, abort, Api, Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity


api = Api(app)
log_post_args = reqparse.RequestParser()
log_post_args.add_argument("id", type=int)
log_post_args.add_argument("time_event", type=datetime)
log_post_args.add_argument("event", type=str)
log_post_args.add_argument("username_report", type=str)
log_post_args.add_argument("time_report", type=str)
log_post_args.add_argument("after_event", type=str)
log_post_args.add_argument("operator", type=str)

switch_port_args = reqparse.RequestParser()
switch_port_args.add_argument("ip", type=str)
switch_port_args.add_argument("port", type=str)


resource_fields = {'id': fields.Integer, 'time_event': fields.DateTime,  'event': fields.String, 'username_report': fields.String, 
                    'time_report': fields.String, 'after_event': fields.String, 'operator': fields.String}


class OperatorLogAdd(Resource):
    @marshal_with(resource_fields)
    @jwt_required()
    def post(self):
        timestamp=int(datetime.today().strftime('%s'))
        current_user = get_jwt_identity()
        args = log_post_args.parse_args()
        if not args['event']:
            abort(404, message="Напишите событие")
        log_oper = OperatorLogModel(time_event=datetime.fromtimestamp(timestamp), event=args['event'], username_report=args['username_report'],
                                    after_event=args['after_event'], time_report=args['time_report'], operator=current_user)
        db.session.add(log_oper)
        db.session.commit()
        return log_oper,  201
    @jwt_required()
    def get(self):
        logs = OperatorLogModel.query.all()
        log_all = {}
        for log in logs:
            log_all[log.id] = {'time_event': log.time_event.strftime('%Y-%m-%d %H:%M'), 'after_event': log.after_event, 'event': log.event,
                               'username_report': log.username_report, 'time_report': log.time_report, 'operator': log.operator}
        return log_all


class OperatorLog(Resource):
    @marshal_with(resource_fields)
    @jwt_required()
    def get(self, log_id):
        log = OperatorLogModel.query.filter_by(id=log_id).first()
        if not log:
            abort(404, message="Net takogo ID")
        return log

    @marshal_with(resource_fields)
    @jwt_required()
    def put(self, log_id):
        current_user = get_jwt_identity()
        args = log_post_args.parse_args()
        log = OperatorLogModel.query.filter_by(id=log_id).first()
        if not log:
            abort(404, message="Net takogo ID")
        if not log.operator == current_user:
            abort(404, message="you don't have permission")
        if args['event']:
            log.event = args['event']
        if args['username_report']:
            log.username_report = args['username_report']
        if args['after_event']:
            log.after_event = args['after_event']
        if args['time_report']:
            log.time_report = args['time_report']
        db.session.commit()
        return log, 201
    @jwt_required()
    def delete(self, log_id):
        log = OperatorLogModel.query.filter_by(id=log_id).first()
        db.session.delete(log)
        db.session.commit()
        return "Log delete", 204

api.add_resource(OperatorLog, '/api/<int:log_id>')
api.add_resource(OperatorLogAdd, '/api')


