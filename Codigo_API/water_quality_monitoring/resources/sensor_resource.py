from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint('sensors', __name__)


from schemas import ActiveSensorSchema, SensorSchema
from models.sensor import SensorModel
from db import db

@blp.route('/sensors')
class SensorList(MethodView):
    @blp.response(200, SensorSchema(many=True))
    def get(self):
        query = SensorModel.query
        from flask import request
        name = request.args.get('name', type=str)
        location = request.args.get('location', type=str)
        sensor_type = request.args.get('type', type=str)
        active = request.args.get('active', type=str)

        if name:
            query = query.filter(SensorModel.name.ilike(name))
        if location:
            query = query.filter(SensorModel.location.ilike(location))
        if sensor_type:
            query = query.filter(SensorModel.sensor_type.ilike(sensor_type))
        if active is not None:
            if active.lower() == 'true':
                query = query.filter(SensorModel.active.is_(True))
            elif active.lower() == 'false':
                query = query.filter(SensorModel.active.is_(False))

        sensors = query.all()
        return sensors

    @blp.arguments(SensorSchema)
    @blp.response(201, SensorSchema)
    def post(self, sensor_data):
        sensor = SensorModel(**sensor_data)
        db.session.add(sensor)
        db.session.commit()
        return sensor

@blp.route('/sensors/<int:id>')
class SensorDetail(MethodView):
    @blp.response(200, SensorSchema)
    def get(self, id):
        sensor = SensorModel.query.get(id)
        if sensor is None:
            abort(404, message="Sensor not found")
        return sensor

    @blp.arguments(ActiveSensorSchema)
    @blp.response(200, SensorSchema)
    def patch(self, update_data, id):
        sensor = SensorModel.query.get(id)
        if sensor is None:
            abort(404, message="Sensor not found")
        sensor.active = update_data['active']
        db.session.commit()
        return sensor