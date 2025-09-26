from marshmallow import Schema, fields

class SensorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    location = fields.Str(required=True)
    sensor_type = fields.Str(required=True)
    installation_date = fields.Date(required=True)
    active = fields.Bool(dump_only=True)
    unit_name = fields.Str(required=True)

class ActiveSensorSchema(Schema):
    active = fields.Bool(required=True)

class MeasurementCreateSchema(Schema):
    sensor_id = fields.Int(required=True)
    value = fields.Float(required=True)
    unit = fields.Str(required=True)

class MeasurementSchema(Schema):
    id = fields.Int(dump_only=True)
    sensor = fields.Nested(SensorSchema)
    date_time = fields.DateTime(required=True)
    value = fields.Float(required=True)
    unit = fields.Str(required=True)