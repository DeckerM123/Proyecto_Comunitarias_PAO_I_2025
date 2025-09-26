from db import db

class SensorModel(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    sensor_type = db.Column(db.String(50), nullable=False)
    installation_date = db.Column(db.Date, nullable=True)
    active = db.Column(db.Boolean, default=True)
    measurements = db.relationship('MeasurementModel', back_populates='sensor', lazy='dynamic')
    unit_name = db.Column(db.String(20), nullable=False)