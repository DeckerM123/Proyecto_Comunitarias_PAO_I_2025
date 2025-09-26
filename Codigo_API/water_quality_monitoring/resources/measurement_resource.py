from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import MeasurementCreateSchema, MeasurementSchema
from models.measurement import MeasurementModel
from models.sensor import SensorModel
from db import db

blp = Blueprint('measurements', __name__)

@blp.route('/measurements')
class Measurement(MethodView):

    @blp.response(200, MeasurementSchema(many=True))
    def get(self):
        query = MeasurementModel.query
        from flask import request
        sensor_id = request.args.get('sensor_id', type=int)
        unit = request.args.get('unit', type=str)

        if sensor_id is not None:
            query = query.filter(MeasurementModel.sensor_id == sensor_id)
        if unit:
            query = query.filter(MeasurementModel.unit.ilike(unit))

        measurements = query.all()
        return measurements

    @blp.arguments(MeasurementCreateSchema)
    @blp.response(201, MeasurementSchema)
    def post(self, measurement_data):
        # Verifica que el sensor exista
        sensor = SensorModel.query.get(measurement_data["sensor_id"])
        if not sensor:
            abort(400, description="Sensor not found")
        if not sensor.active:
            abort(400, description="Cannot register measurement: sensor is not active")
        from datetime import datetime
        measurement = MeasurementModel(**measurement_data)
        measurement.date_time = datetime.now()
        db.session.add(measurement)
        db.session.commit()
        return measurement

@blp.route('/measurements/<int:id>')
class MeasurementDetail(MethodView):
    @blp.response(200, MeasurementSchema)
    def get(self, id):
        measurement = MeasurementModel.query.get_or_404(id)
        return measurement